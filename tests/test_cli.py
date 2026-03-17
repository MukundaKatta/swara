"""Tests for the CLI interface."""

from click.testing import CliRunner

from swara.cli import cli


class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_version(self):
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_list_ragas(self):
        result = self.runner.invoke(cli, ["list-ragas"])
        assert result.exit_code == 0
        assert "Yaman" in result.output

    def test_list_taals(self):
        result = self.runner.invoke(cli, ["list-taals"])
        assert result.exit_code == 0
        assert "Teentaal" in result.output

    def test_list_bols(self):
        result = self.runner.invoke(cli, ["list-bols"])
        assert result.exit_code == 0
        assert "teentaal_theka" in result.output

    def test_compose(self):
        result = self.runner.invoke(cli, [
            "compose", "--raga", "yaman", "--taal", "teentaal",
            "--laya", "madhya", "--duration", "5", "--seed", "42",
        ])
        assert result.exit_code == 0
        assert "Yaman" in result.output

    def test_compose_invalid_raga(self):
        result = self.runner.invoke(cli, [
            "compose", "--raga", "nonexistent",
        ])
        assert result.exit_code != 0

    def test_report(self):
        result = self.runner.invoke(cli, [
            "report", "--raga", "yaman", "--taal", "teentaal",
        ])
        assert result.exit_code == 0
        assert "Yaman" in result.output

    def test_raga_info(self):
        result = self.runner.invoke(cli, ["raga-info", "--raga", "bhairav"])
        assert result.exit_code == 0
        assert "Bhairav" in result.output

    def test_jugalbandi(self):
        result = self.runner.invoke(cli, [
            "jugalbandi", "--raga", "yaman", "--duration", "5",
        ])
        assert result.exit_code == 0
