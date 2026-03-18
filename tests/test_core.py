"""Tests for Swara."""
from src.core import Swara
def test_init(): assert Swara().get_stats()["ops"] == 0
def test_op(): c = Swara(); c.compose(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Swara(); [c.compose() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Swara(); c.compose(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Swara(); r = c.compose(); assert r["service"] == "swara"
