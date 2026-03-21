"""Tests for modularity validation."""

from pathlib import Path

from abcdef.modularity.modularity import Modularity


class TestValidation:
    """Validation tests using the validation_boundary_valid fixture."""

    def test_validate_passes_for_valid_boundary_structure(self) -> None:
        """validate() returns no violations for a valid modular structure."""
        fixture_root = Path(__file__).parent / "fixtures" / "validation_boundary_valid"
        modularity = Modularity(fixture_root)
        modularity.discover()
        violations = modularity.validate()
        assert violations == [], f"Expected no violations, got {violations}"
