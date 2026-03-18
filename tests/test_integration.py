"""Integration tests for Swara."""
from src.core import Swara

class TestSwara:
    def setup_method(self):
        self.c = Swara()
    def test_10_ops(self):
        for i in range(10): self.c.compose(i=i)
        assert self.c.get_stats()["ops"] == 10
    def test_service_name(self):
        assert self.c.compose()["service"] == "swara"
    def test_different_inputs(self):
        self.c.compose(type="a"); self.c.compose(type="b")
        assert self.c.get_stats()["ops"] == 2
    def test_config(self):
        c = Swara(config={"debug": True})
        assert c.config["debug"] is True
    def test_empty_call(self):
        assert self.c.compose()["ok"] is True
    def test_large_batch(self):
        for _ in range(100): self.c.compose()
        assert self.c.get_stats()["ops"] == 100
