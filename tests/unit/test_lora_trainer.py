import numpy as np

from src.training.lora_trainer import LoRATrainer


def test_lora_trainer_runs() -> None:
    trainer = LoRATrainer(
        base_model_path="models/cosyvoice/",
        speaker_embedding=np.ones((256,), dtype=np.float32),
        data_dir="data/training",
        checkpoint_dir="models/lora",
        config=object(),
        device="cpu",
    )
    history = trainer.train(epochs=1)
    assert len(history.train_loss) == 1
