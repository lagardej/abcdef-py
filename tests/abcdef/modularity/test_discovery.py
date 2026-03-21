"""Tests for module discovery."""

from pathlib import Path

from abcdef.modularity.modularity import Modularity


class TestDiscovery:
    """Test module discovery against the validation_boundary_valid fixture."""

    def test_discovers_only_module_packages(self) -> None:
        """Should discover only module_a and module_b (excluding shared package)."""
        fixture_root = Path(__file__).parent / "fixtures" / "validation_boundary_valid"
        modularity = Modularity(fixture_root)
        modules = modularity.discover()

        module_names = {m.declaration.name for m in modules}
        assert module_names == {"module_a", "module_b", "module_c"}, (
            f"Expected modules {{module_a, module_b, module_c}}, got {module_names}"
        )

    def test_discovers_nothing_from_non_module_packages(self) -> None:
        """Should discover no modules when packages lack __modularity__ declarations."""
        fixture_root = Path(__file__).parent / "fixtures" / "only_non_modules"
        modularity = Modularity(fixture_root)
        modules = modularity.discover()
        module_names = [m.declaration.name for m in modules]
        assert modules == [], f"Expected no modules, got {module_names}"
