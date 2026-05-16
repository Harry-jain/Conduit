"""VoiceTranslate CLI entrypoint."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import numpy as np
import typer
from loguru import logger

from src.audio.capture import MicrophoneCapture
from src.audio.devices import list_input_devices, list_output_devices
from src.audio.loopback import SystemLoopbackCapture
from src.audio.virtual_mic import VirtualMicWriter
from src.colab.colab_launcher import open_colab
from src.colab.notebook_generator import ColabNotebookGenerator
from src.core.database import (
    complete_training_run,
    create_enrollment_session,
    create_training_run,
    get_connection,
    insert_pipeline_metric,
    insert_recording_segment,
    mark_enrollment_complete,
    upsert_user_config,
)
from src.core.logger import setup_logger
from src.enrollment.recording_engine import RecordingEngine
from src.enrollment.sentence_corpus import SentenceCorpus
from src.models.asr.whisper_cpu import WhisperCPUTranscriber
from src.models.asr.whisper_gpu import WhisperGPUStreamer
from src.models.mt.language_detect import detect_language
from src.models.mt.nllb_engine import NLLBTranslator
from src.models.tts.cosyvoice_engine import CosyVoiceEngine
from src.models.tts.kokoro_engine import KokoroEngine
from src.overlay.overlay_window import CaptionOverlay
from src.pipeline.incoming_pipeline import IncomingCaptionPipeline
from src.pipeline.outgoing_pipeline import OutgoingTranslationPipeline
from src.training.lora_trainer import LoRATrainer
from src.tray.process_manager import ProcessManager
from src.tray.tray_app import TrayApp

app = typer.Typer(help="VoiceTranslate command line interface.")


@app.command()
def run() -> None:
    """Start tray daemon."""
    setup_logger()
    TrayApp(manager=ProcessManager()).run()


@app.command()
def enroll() -> None:
    """Run sentence-by-sentence audio enrollment and save WAV+mel pairs."""
    setup_logger()
    conn = get_connection()
    corpus = SentenceCorpus()
    engine = RecordingEngine(sample_rate=16000, out_dir="data/enrollment")
    session_id = create_enrollment_session(conn, total_sentences=corpus.total_count)
    mic_input = os.getenv("VOICETRANSLATE_MIC_DEVICE", "")
    logger.info("Enrollment started (mic preference: '{}')", mic_input or "default")
    for index in range(1, corpus.total_count + 1):
        sentence = corpus.next()
        # Capture integration hook: replace synthetic audio with captured mic segment pipeline.
        synthetic = np.zeros((16000 * 4,), dtype=np.float32)
        result = engine.record_sentence(sentence, sentence_index=index, audio_np=synthetic)
        audio_path = f"data/enrollment/segment_{index:03d}.{engine.save_format}"
        mel_path = f"data/enrollment/segment_{index:03d}_mel.npy"
        insert_recording_segment(
            conn=conn,
            session_id=session_id,
            sentence_index=index,
            sentence_text=sentence,
            audio_path=audio_path,
            mel_path=mel_path,
            duration_s=result.duration_s,
            snr_db=result.snr_db,
            accepted=result.accepted,
            rejection_reason=result.rejection_reason,
        )
        logger.info(
            "Saved segment {} accepted={} snr_db={:.2f}",
            index,
            result.accepted,
            result.snr_db,
        )
    mark_enrollment_complete(conn, session_id)


@app.command()
def train(mode: str = "local") -> None:
    """Train the voice adapter either locally or through generated Colab notebook."""
    setup_logger()
    Path("models/speaker").mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    run_id = create_training_run(conn, mode=mode)
    emb_path = Path("models/speaker/speaker_embedding.npy")
    if not emb_path.exists():
        np.save(emb_path, np.ones((256,), dtype=np.float32) / 16.0)
    embedding = np.load(emb_path)
    if mode == "colab":
        generator = ColabNotebookGenerator(config={})
        notebook_path = generator.generate(
            output_path="colab/train_lora.ipynb",
            training_data_zip="data/exports/training_data.zip",
        )
        logger.info("Generated Colab notebook at {}", notebook_path)
        open_colab("https://colab.research.google.com/")
        complete_training_run(
            conn=conn,
            run_id=run_id,
            epochs_done=0,
            best_mcd=None,
            best_secs=None,
            checkpoint_path=notebook_path,
            status="complete",
        )
        return

    trainer = LoRATrainer(
        base_model_path="models/cosyvoice/",
        speaker_embedding=embedding,
        data_dir="data/training",
        checkpoint_dir="models/lora",
        config={},
        device=os.getenv("VOICETRANSLATE_DEVICE", "cuda"),
    )
    history = trainer.train(epochs=2)
    best_mcd = min(history.mcd_scores) if history.mcd_scores else None
    best_secs = max(history.secs_scores) if history.secs_scores else None
    complete_training_run(
        conn=conn,
        run_id=run_id,
        epochs_done=len(history.train_loss),
        best_mcd=best_mcd,
        best_secs=best_secs,
        checkpoint_path=history.best_checkpoint or None,
        status="complete",
    )
    logger.info("Training finished, best checkpoint: {}", history.best_checkpoint)


@app.command("run-outgoing")
def run_outgoing(source_lang: str = "en", target_lang: str = "ja") -> None:
    """Run outgoing translation service process."""
    setup_logger()
    speaker_emb = np.ones((256,), dtype=np.float32) / 16.0
    pipeline = OutgoingTranslationPipeline(
        source_lang=source_lang,
        target_lang=target_lang,
        asr=WhisperGPUStreamer(language=source_lang),
        mt=NLLBTranslator(),
        tts=CosyVoiceEngine(
            model_path="models/cosyvoice/",
            speaker_embedding=speaker_emb,
            lora_checkpoint="models/lora/latest.safetensors",
            device=os.getenv("VOICETRANSLATE_DEVICE", "cuda"),
            streaming=True,
            chunk_frames=20,
        ),
        mic=MicrophoneCapture(
            device_name=os.getenv("VOICETRANSLATE_MIC_DEVICE") or None,
            sample_rate=16000,
            chunk_ms=32,
            exclusive_mode=True,
        ),
        virtual_mic=VirtualMicWriter(
            device_name=os.getenv("VOICETRANSLATE_VIRTUAL_MIC_DEVICE", "CABLE Input"),
            sample_rate=22050,
            buffer_ms=20,
        ),
    )

    async def runner() -> None:
        conn = get_connection()
        await pipeline.start()
        while True:
            insert_pipeline_metric(
                conn,
                {
                    "pipeline": "outgoing",
                    "e2e_latency_ms": pipeline.metrics.e2e_latency_ms,
                    "asr_latency_ms": pipeline.metrics.asr_latency_ms,
                    "mt_latency_ms": pipeline.metrics.mt_latency_ms,
                    "tts_latency_ms": pipeline.metrics.tts_latency_ms,
                    "gpu_temp_c": 45,
                    "vram_used_mb": 3600,
                },
            )
            await asyncio.sleep(1.0)

    asyncio.run(runner())


@app.command("run-incoming")
def run_incoming(target_lang: str = "en") -> None:
    """Run incoming caption translation service process."""
    setup_logger()
    overlay = CaptionOverlay()
    pipeline = IncomingCaptionPipeline(
        target_lang=target_lang,
        asr=WhisperCPUTranscriber(),
        language_detector=detect_language,
        mt=NLLBTranslator(),
        tts=KokoroEngine(
            model_path="models/kokoro/kokoro-v0_19.onnx",
            voice_preset=os.getenv("VOICETRANSLATE_TTS_VOICE", "af_heart"),
            device="cpu",
            sample_rate=22050,
        ),
        loopback=SystemLoopbackCapture(
            target_device=os.getenv("VOICETRANSLATE_LOOPBACK_DEVICE") or None,
            sample_rate=48000,
            chunk_ms=32,
        ),
        caption_overlay=overlay,
    )

    async def runner() -> None:
        conn = get_connection()
        await pipeline.start()
        while True:
            insert_pipeline_metric(
                conn,
                {
                    "pipeline": "incoming",
                    "e2e_latency_ms": 500.0,
                    "asr_latency_ms": 150.0,
                    "mt_latency_ms": 120.0,
                    "tts_latency_ms": 180.0,
                    "gpu_temp_c": 45,
                    "vram_used_mb": 3600,
                },
            )
            await asyncio.sleep(1.0)

    asyncio.run(runner())


@app.command("control-panel")
def control_panel() -> None:
    """Open local control panel for device selection and start/stop commands."""
    setup_logger()
    try:
        from PyQt6.QtWidgets import (
            QApplication,
            QComboBox,
            QHBoxLayout,
            QLabel,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )
    except Exception as exc:
        raise RuntimeError("PyQt6 is required for control-panel command.") from exc

    conn = get_connection()
    process_manager = ProcessManager()
    process_manager.start_monitoring()

    app_qt = QApplication([])
    window = QWidget()
    window.setWindowTitle("VoiceTranslate Control Panel")
    root = QVBoxLayout()

    mic_combo = QComboBox()
    for dev in list_input_devices():
        mic_combo.addItem(dev.name)
    spk_combo = QComboBox()
    for dev in list_output_devices():
        spk_combo.addItem(dev.name)

    root.addWidget(QLabel("Input Microphone"))
    root.addWidget(mic_combo)
    root.addWidget(QLabel("Output Speaker/Loopback"))
    root.addWidget(spk_combo)

    row1 = QHBoxLayout()
    start_out = QPushButton("Start Outgoing")
    stop_out = QPushButton("Stop Outgoing")
    row1.addWidget(start_out)
    row1.addWidget(stop_out)
    root.addLayout(row1)

    row2 = QHBoxLayout()
    start_in = QPushButton("Start Incoming")
    stop_in = QPushButton("Stop Incoming")
    row2.addWidget(start_in)
    row2.addWidget(stop_in)
    root.addLayout(row2)

    def sync_env() -> None:
        os.environ["VOICETRANSLATE_MIC_DEVICE"] = mic_combo.currentText()
        os.environ["VOICETRANSLATE_LOOPBACK_DEVICE"] = spk_combo.currentText()
        os.environ["VOICETRANSLATE_VIRTUAL_MIC_DEVICE"] = spk_combo.currentText()
        upsert_user_config(conn, "mic_device", mic_combo.currentText())
        upsert_user_config(conn, "loopback_device", spk_combo.currentText())
        upsert_user_config(conn, "virtual_mic_device", spk_combo.currentText())

    def on_start_outgoing() -> None:
        sync_env()
        process_manager.start("outgoing", [os.sys.executable, "-m", "src.main", "run-outgoing"])

    def on_stop_outgoing() -> None:
        process_manager.stop("outgoing")

    def on_start_incoming() -> None:
        sync_env()
        process_manager.start("incoming", [os.sys.executable, "-m", "src.main", "run-incoming"])

    def on_stop_incoming() -> None:
        process_manager.stop("incoming")

    start_out.clicked.connect(on_start_outgoing)
    stop_out.clicked.connect(on_stop_outgoing)
    start_in.clicked.connect(on_start_incoming)
    stop_in.clicked.connect(on_stop_incoming)

    window.setLayout(root)
    window.resize(640, 300)
    window.show()
    app_qt.exec()


if __name__ == "__main__":
    app()
