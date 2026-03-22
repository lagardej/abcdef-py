"""Tests for MarkdownReporter."""

import sys
from pathlib import Path

from abcdef.modularity import Modularity


def test_documentation_matches_expected() -> None:
    """Compare generated documentation to expected fixture."""
    # Ensure fixtures/business_module_docs can be imported as top-level package
    fixtures_dir = str(Path(__file__).parent / "fixtures")
    if fixtures_dir not in sys.path:
        sys.path.insert(0, fixtures_dir)

    fixture_root = Path(__file__).parent / "fixtures" / "business_app"
    mod = Modularity(fixture_root)
    mod.discover()
    actual = mod.document()

    expected_path = Path(__file__).parent / "fixtures" / "business_module_doc_single" / "modules.md"
    expected = expected_path.read_text(encoding="utf-8")

    assert actual == expected, "Generated documentation does not match expected output"
