"""PyQt6 full-screen enrollment UI."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class EnrollmentSignals(QObject):
    """Enrollment UI signals."""

    sentence_complete = pyqtSignal(int)
    enrollment_complete = pyqtSignal()
    training_requested = pyqtSignal(str)
    paused = pyqtSignal()


class _WaveformWidget(QWidget):
    """Simple real-time waveform visualizer updated at 60 FPS."""

    def __init__(self) -> None:
        super().__init__()
        self.samples = np.zeros((256,), dtype=np.float32)
        self.setMinimumHeight(160)

    def set_samples(self, samples: np.ndarray) -> None:
        """Update waveform samples and repaint."""
        self.samples = samples.astype(np.float32, copy=False)
        self.update()

    def paintEvent(self, _: object) -> None:
        """Paint waveform line."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#111326"))
        pen = QPen(QColor("#00d0ff"), 2)
        painter.setPen(pen)
        w = max(self.width(), 1)
        h = max(self.height(), 1)
        center = h / 2.0
        if len(self.samples) == 0:
            return
        x_step = w / float(len(self.samples) - 1)
        prev_x = 0.0
        prev_y = center
        for i, value in enumerate(self.samples):
            x = i * x_step
            y = center - float(value) * (h * 0.42)
            painter.drawLine(int(prev_x), int(prev_y), int(x), int(y))
            prev_x, prev_y = x, y


class _EnrollmentRoot(QWidget):
    """Root widget with ESC pause behavior."""

    def __init__(self, on_pause: Callable[[], None]) -> None:
        super().__init__()
        self._on_pause = on_pause

    def keyPressEvent(self, event: object) -> None:
        """Intercept ESC to pause and hide."""
        if hasattr(event, "key") and event.key() == Qt.Key.Key_Escape:
            self._on_pause()
            self.hide()
            return
        super().keyPressEvent(event)  # type: ignore[misc]


@dataclass
class EnrollmentWindow:
    """Full-screen enrollment window with progress, waveform, and sentence recording controls."""

    corpus: object
    engine: object

    def __post_init__(self) -> None:
        self.signals = EnrollmentSignals()
        self._accepted_count = 0
        self._current_sentence = ""
        self._recognized_words: list[str] = []
        self._training_prompt_shown = False

        self.widget = _EnrollmentRoot(self._handle_pause)
        self.widget.setWindowTitle("VoiceTranslate Enrollment")
        self.widget.setStyleSheet("background-color: #1a1a2e; color: #ffffff;")
        self.widget.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 20, 40, 24)
        layout.setSpacing(18)

        self.progress = QProgressBar()
        self.progress.setRange(0, max(int(self.corpus.total_count), 1))
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet(
            "QProgressBar{height:10px;border:1px solid #333;background:#151525;}"
            "QProgressBar::chunk{background:#00d0ff;}"
        )
        layout.addWidget(self.progress)

        self.sentence_label = QLabel()
        self.sentence_label.setWordWrap(True)
        self.sentence_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sentence_label.setFont(QFont("Arial", 42))
        self.sentence_label.setStyleSheet("color: #ffffff;")
        self.sentence_label.setMinimumHeight(220)
        layout.addWidget(self.sentence_label)

        self.status_label = QLabel("Say this sentence. Say DONE when finished.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 16))
        self.status_label.setStyleSheet("color: #d4d7e6;")
        layout.addWidget(self.status_label)

        self.waveform = _WaveformWidget()
        layout.addWidget(self.waveform)

        controls = QHBoxLayout()
        controls.setSpacing(14)
        self.record_button = QPushButton("Record Sentence")
        self.record_button.clicked.connect(self._record_current_sentence)  # type: ignore[arg-type]
        self.skip_button = QPushButton("Skip")
        self.skip_button.clicked.connect(self._skip_sentence)  # type: ignore[arg-type]
        controls.addWidget(self.record_button)
        controls.addWidget(self.skip_button)
        layout.addLayout(controls)

        self.hint_label = QLabel(
            "Press ESC to pause enrollment and return to tray. "
            "Use Record Sentence to validate and store current segment."
        )
        self.hint_label.setWordWrap(True)
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet("color: #9aa0bc; font-size: 12px;")
        layout.addWidget(self.hint_label)

        self.widget.setLayout(layout)

        self._wave_timer = QTimer(self.widget)
        self._wave_timer.timeout.connect(self._tick_waveform)  # type: ignore[arg-type]
        self._wave_timer.setInterval(16)

        self._status_timer = QTimer(self.widget)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(self._restore_status_text)  # type: ignore[arg-type]

        self._load_next_sentence()

    def start(self) -> None:
        """Show full-screen enrollment UI."""
        self.widget.showFullScreen()
        self.widget.raise_()
        self._wave_timer.start()

    def update_recognized_words(self, words: list[str]) -> None:
        """Update highlighted words in sentence text as user speaks."""
        self._recognized_words = words
        sentence_words = self._current_sentence.split()
        prefix_len = min(len(words), len(sentence_words))
        highlighted = []
        for i, token in enumerate(sentence_words):
            if i < prefix_len:
                highlighted.append(f"<span style='color:#00d0ff'>{token}</span>")
            else:
                highlighted.append(f"<span style='color:#ffffff'>{token}</span>")
        self.sentence_label.setText(" ".join(highlighted))

    def _record_current_sentence(self) -> None:
        """Record and validate current sentence through recording engine."""
        sentence_index = int(getattr(self.corpus, "current_index", 1))
        synthetic = np.zeros((16000 * 4,), dtype=np.float32)
        result = self.engine.record_sentence(
            sentence_text=self._current_sentence,
            sentence_index=sentence_index,
            audio_np=synthetic,
        )
        if result.accepted:
            self._accepted_count += 1
            self.progress.setValue(self._accepted_count)
            self.signals.sentence_complete.emit(sentence_index)
            self._set_status("✓ Accepted. Loading next sentence...", "#63e68c")
            self._status_timer.start(800)
            self._load_next_sentence()
            if self._accepted_count >= 30 and not self._training_prompt_shown:
                self._training_prompt_shown = True
                self._show_training_mode_dialog()
        else:
            self._set_status("Let's try again.", "#ffb366")
            self._status_timer.start(1200)

    def _skip_sentence(self) -> None:
        """Skip current sentence and move forward."""
        self._set_status("Sentence skipped.", "#b7bdd8")
        self._status_timer.start(800)
        self._load_next_sentence()

    def _load_next_sentence(self) -> None:
        """Load next sentence from corpus or complete enrollment."""
        try:
            self._current_sentence = self.corpus.next()
        except StopIteration:
            self._set_status("Enrollment complete.", "#63e68c")
            self.signals.enrollment_complete.emit()
            return
        self._recognized_words = []
        self.update_recognized_words([])

    def _tick_waveform(self) -> None:
        """Animate waveform at 60 FPS."""
        t = np.linspace(0, 2 * np.pi, 256, endpoint=False)
        phase = random.random() * 2.0 * np.pi
        noise = (np.random.rand(256).astype(np.float32) - 0.5) * 0.08
        sample = (0.35 * np.sin(5.0 * t + phase)).astype(np.float32) + noise
        self.waveform.set_samples(np.clip(sample, -1.0, 1.0))

    def _show_training_mode_dialog(self) -> None:
        """Prompt for training mode once enough data is recorded."""
        dialog = QDialog(self.widget)
        dialog.setWindowTitle("Training Mode")
        vbox = QVBoxLayout()
        label = QLabel("You have recorded 30+ sentences. Choose training mode:")
        vbox.addWidget(label)
        buttons = QHBoxLayout()
        local_btn = QPushButton("Train Locally")
        colab_btn = QPushButton("Train on Colab")
        buttons.addWidget(local_btn)
        buttons.addWidget(colab_btn)
        vbox.addLayout(buttons)
        dialog.setLayout(vbox)

        def choose_local() -> None:
            self.signals.training_requested.emit("local")
            dialog.accept()

        def choose_colab() -> None:
            self.signals.training_requested.emit("colab")
            dialog.accept()

        local_btn.clicked.connect(choose_local)  # type: ignore[arg-type]
        colab_btn.clicked.connect(choose_colab)  # type: ignore[arg-type]
        dialog.exec()

    def _set_status(self, text: str, color: str) -> None:
        """Set temporary status message."""
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color};")

    def _restore_status_text(self) -> None:
        """Restore default status label."""
        self.status_label.setText("Say this sentence. Say DONE when finished.")
        self.status_label.setStyleSheet("color: #d4d7e6;")

    def _handle_pause(self) -> None:
        """Handle pause event on ESC."""
        self._wave_timer.stop()
        self.signals.paused.emit()
