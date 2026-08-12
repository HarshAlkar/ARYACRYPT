import pytest
from app.framework.aryabhata.mapping import AryabhataMapping


class TestAryabhataMapping:
    """
    Unit tests for the AryabhataMapping class, which is responsible 
    for the bidirectional mapping between numeric Base-100 components 
    and their Roman Sanskrit phonetic symbols.
    """

    @pytest.fixture
    def mapper(self):
        """Fixture providing a fresh instance of AryabhataMapping for each test."""
        return AryabhataMapping()

    def test_initialization(self, mapper):
        """Test that the internal dictionaries map correctly from defaults."""
        assert len(mapper._varga_to_sym) == 25, "Should have 25 Varga consonants"
        assert len(mapper._avarga_to_sym) == 8, "Should have 8 Avarga consonants"
        
        # Test bidirectional consistency
        assert len(mapper._sym_to_varga_val) == 25
        assert len(mapper._sym_to_avarga_val) == 8

    def test_get_varga_symbol_valid(self, mapper):
        """Ensure valid Varga numbers map to correct symbols."""
        assert mapper.get_varga_symbol(1) == 'k'
        assert mapper.get_varga_symbol(25) == 'm'
        
    def test_get_varga_symbol_invalid(self, mapper):
        """Ensure invalid Varga numbers safely return None."""
        assert mapper.get_varga_symbol(0) is None
        assert mapper.get_varga_symbol(26) is None
        assert mapper.get_varga_symbol(-5) is None
        
    def test_get_avarga_symbol_valid(self, mapper):
        """Ensure valid Avarga tens map to correct symbols."""
        assert mapper.get_avarga_symbol(30) == 'y'
        assert mapper.get_avarga_symbol(100) == 'h'
        
    def test_get_avarga_symbol_invalid(self, mapper):
        """Ensure invalid Avarga numbers safely return None."""
        assert mapper.get_avarga_symbol(20) is None   # Below threshold
        assert mapper.get_avarga_symbol(35) is None   # Not a clean multiple of 10
        assert mapper.get_avarga_symbol(110) is None  # Above threshold

    def test_get_vowel_symbol(self, mapper):
        """Ensure positional vowel indices map correctly."""
        assert mapper.get_vowel_symbol(0) == 'a'
        assert mapper.get_vowel_symbol(8) == 'au'
        
        # Out of bounds indices should return None
        assert mapper.get_vowel_symbol(9) is None
        assert mapper.get_vowel_symbol(-1) is None

    def test_reverse_mapping_varga(self, mapper):
        """Test reverse string lookup for Varga values."""
        assert mapper.get_varga_value('k') == 1
        assert mapper.get_varga_value('m') == 25
        assert mapper.get_varga_value('invalid') is None
        assert mapper.get_varga_value('') is None

    def test_reverse_mapping_avarga(self, mapper):
        """Test reverse string lookup for Avarga values."""
        assert mapper.get_avarga_value('y') == 30
        assert mapper.get_avarga_value('h') == 100
        assert mapper.get_avarga_value('invalid') is None
        assert mapper.get_avarga_value('') is None
