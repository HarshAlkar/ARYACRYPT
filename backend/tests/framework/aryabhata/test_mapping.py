from aryacrypt.mapping import AryabhataMapping


class TestAryabhataMapping:
    def test_initialization(self):
        mapper = AryabhataMapping()
        assert len(mapper._varga_val_to_sym) == 25
        assert len(mapper._avarga_val_to_sym) == 8
        assert mapper.get_varga_symbol(1) == "k"
        assert mapper.get_avarga_symbol(30) == "y"

    def test_get_varga_symbol_valid(self):
        mapper = AryabhataMapping()
        assert mapper.get_varga_symbol(1) == "k"
        assert mapper.get_varga_symbol(25) == "m"

    def test_get_varga_symbol_invalid(self):
        mapper = AryabhataMapping()
        assert mapper.get_varga_symbol(0) is None
        assert mapper.get_varga_symbol(26) is None

    def test_get_avarga_symbol_valid(self):
        mapper = AryabhataMapping()
        assert mapper.get_avarga_symbol(30) == "y"
        assert mapper.get_avarga_symbol(100) == "h"

    def test_get_vowel_symbol(self):
        mapper = AryabhataMapping()
        assert mapper.get_vowel_symbol(0) == "a"
        assert mapper.get_vowel_symbol(8) == "au"
        assert mapper.get_vowel_symbol(9) is None
