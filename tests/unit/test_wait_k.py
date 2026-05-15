from src.models.mt.wait_k import WaitKPolicy


def test_wait_k_policy() -> None:
    policy = WaitKPolicy(k=4)
    emits = [policy.should_emit() for _ in range(10)]
    assert emits[2] is False
    assert emits[3] is True
