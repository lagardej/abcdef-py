"""Tests for abcdef.modularity — marker constants."""

from abcdef.modularity.markers import COMMAND_MODULE, QUERY_MODULE, SPI


class TestMarkerConstants:
    """Verify marker constants are defined."""

    def test_command_module_constant(self) -> None:
        """COMMAND_MODULE constant has correct value."""
        assert COMMAND_MODULE == "command_module"

    def test_query_module_constant(self) -> None:
        """QUERY_MODULE constant has correct value."""
        assert QUERY_MODULE == "query_module"

    def test_spi_constant(self) -> None:
        """SPI constant has correct value."""
        assert SPI == "spi"
