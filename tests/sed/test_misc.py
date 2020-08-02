# pylint: disable=protected-access

import pytest

from coreutils import sed
from coreutils.sed import SedFlags


@pytest.mark.skip(reason='TODO: move to search')
@pytest.mark.parametrize(
    'command, expected',
    [
        ('probably', True),
        ('perdak', False),
        (r'\w+ s c.*d', True),
        (r'\d.*', False),
        (lambda text: True, True),
        (lambda text: False, False),
        (lambda text: 'substitute' in text, True),
        (lambda text: 'substitute' not in text, False),
    ],
)
def test_match_command(command, expected):
    string = 'The s command (as in substitute) is probably'
    result = sed._match_line(string, command, flags=frozenset())
    assert result == expected


@pytest.mark.skip(reason='no way of currently testing this')
@pytest.mark.parametrize(
    'flag, expected',
    [
        (None, True),
        (SedFlags.GLOBAL, False),
        (SedFlags.PRINT, False),
        (SedFlags.INSENSITIVE, False),
        (SedFlags.DELETE, False),
    ],
)
def test_match_with_flag(flag, expected):
    string = 'The s command (as in substitute) is probably'
    command = 'The s c.*d'
    result = sed._match_line(string, command, flags={flag})
    assert result == expected


@pytest.mark.skip(reason='no way of currently testing this')
@pytest.mark.parametrize(
    'flags, expected',
    [
        (frozenset({SedFlags.GLOBAL, SedFlags.PRINT}), False),
        (frozenset({SedFlags.DELETE, SedFlags.INSENSITIVE}), False),
    ],
)
def test_match_with_several_flags(flags, expected):
    string = 'The s command (as in substitute) is probably'
    command = 'The s c.*d'
    result = sed._match_line(string, command, flags=flags)
    assert result == expected
