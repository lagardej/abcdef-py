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

    def test_validate_detects_facade_rule_violation(self) -> None:
        """Facade rule violation: module exports internal symbols."""
        fixture_root = Path(__file__).parent / "fixtures" / "facade_violation"
        modularity = Modularity(fixture_root)
        modularity.discover()
        violations = modularity.validate()
        assert len(violations) > 0, "Expected at least one violation"
        assert any(v.violation_type == "facade_rule" for v in violations), (
            f"Expected facade_rule violation, got {violations}"
        )

    def test_validate_detects_import_boundary_violation(self) -> None:
        """Import boundary violation: module imports from another module's internal."""
        fixture_root = Path(__file__).parent / "fixtures" / "import_boundary_violation"
        modularity = Modularity(fixture_root)
        modularity.discover()
        violations = modularity.validate()
        assert len(violations) > 0, "Expected at least one violation"
        assert any(v.violation_type == "import_boundary" for v in violations), (
            f"Expected import_boundary violation, got {violations}"
        )
