from pathlib import Path

from dmatlas.cli import main


ROOT = Path(__file__).resolve().parents[1]


def test_validate_passes():
    assert main(["validate"]) == 0


def test_report_writes_summary():
    assert main(["report"]) == 0
    summary = ROOT / "dashboards" / "summary.json"
    assert summary.exists()


def test_analyze_writes_pilot_output():
    assert main(["analyze"]) == 0
    pilot = ROOT / "dashboards" / "pilot_agd_craniofacial.json"
    assert pilot.exists()


def test_quality_writes_data_quality_output():
    assert main(["quality"]) == 0
    quality = ROOT / "dashboards" / "data_quality.json"
    assert quality.exists()


def test_standards_writes_standards_output():
    assert main(["standards"]) == 0
    standards = ROOT / "dashboards" / "standards.json"
    assert standards.exists()
