"""Benchmark tests for Swara."""
import time, pytest
from src.core import Swara

def test_1000_ops_under_1s():
    c = Swara()
    start = time.time()
    for i in range(1000):
        c.compose(i=i)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"1000 ops took {elapsed:.2f}s"
    assert c.get_stats()["ops"] == 1000

def test_accuracy_at_scale():
    c = Swara()
    for i in range(500):
        r = c.compose(i=i)
        assert r["ok"] is True
        assert r["n"] == i + 1

def test_reset_is_instant():
    c = Swara()
    for _ in range(100): c.compose()
    start = time.time()
    c.reset()
    elapsed = time.time() - start
    assert elapsed < 0.01
    assert c.get_stats()["ops"] == 0

def test_memory_stable():
    """Ensure no memory leaks after reset."""
    c = Swara()
    for _ in range(1000): c.compose(data="x" * 100)
    c.reset()
    assert c.get_stats()["ops"] == 0
    assert c.get_stats()["log_size"] == 0
