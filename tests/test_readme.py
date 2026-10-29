"""The README never names a model: models are added and retired, so examples use MODEL_ID and link the live catalog."""
import re
from pathlib import Path

README = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")


def test_readme_names_no_model():
    assert not re.search(r"empiriolabs/(?!MODEL_ID\b)[a-z0-9]", README), "use empiriolabs/MODEL_ID in examples"


def test_readme_links_the_live_catalog():
    assert "https://empiriolabs.ai/models" in README
