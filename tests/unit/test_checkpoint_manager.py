from src.training.checkpoint_manager import CheckpointManager


def test_checkpoint_save_load(tmp_path) -> None:
    mgr = CheckpointManager(checkpoint_dir=str(tmp_path))
    path = mgr.save({"x": 1}, epoch=1, step=2)
    loaded = mgr.load(path)
    assert loaded["x"] == 1
