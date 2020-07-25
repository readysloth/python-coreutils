import pytest

from coreutils import sed
from coreutils.sed import SedFlags


class TestSedMisc:
    @pytest.mark.parametrize(
        'command, expected',
        [
            ('probably', True),
            ('perdak', False,),
            (r'\w+ s c.*d', True),
            (r'\d.*', False),
            (lambda l: True, True,),
            (lambda l: False, False,),
            (lambda l: 'substitute' in l, True,),
            (lambda l: 'substitute' not in l, False,),
        ],
    )
    def test_match_command(self, command, expected):
        string = 'The s command (as in substitute) is probably'
        result = sed.match_string(string, command)
        assert result == expected

    @pytest.mark.skip(reason='no way of currently testing this')
    @pytest.mark.parametrize(
        'flag, expected',
        [
            (None, True),
            (SedFlags.GLOBAL, False),
            (SedFlags.PRINT, False),
            (SedFlags.EXECUTE, False),
            (SedFlags.INSENSITIVE, False),
            (SedFlags.DELETE, False),
        ],
    )
    def test_match_with_flag(self, flag, expected):
        string = 'The s command (as in substitute) is probably'
        command = 'The s c.*d'
        result = sed.match_string(string, command, flags={flag})
        assert result == expected

    @pytest.mark.skip(reason='no way of currently testing this')
    @pytest.mark.parametrize(
        'flags, expected',
        [
            (frozenset({SedFlags.GLOBAL, SedFlags.PRINT}), False),
            (frozenset({SedFlags.DELETE, SedFlags.EXECUTE, SedFlags.INSENSITIVE}), False),
        ],
    )
    def test_match_with_several_flags(self, flags, expected):
        string = 'The s command (as in substitute) is probably'
        command = 'The s c.*d'
        result = sed.match_string(string, command, flags=flags)
        assert result == expected
