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
            ({SedFlags.GLOBAL, SedFlags.PRINT}, False),
            ({SedFlags.DELETE, SedFlags.EXECUTE, SedFlags.INSENSITIVE}, False),
        ],
    )
    def test_match_with_several_flags(self, flags, expected):
        string = 'The s command (as in substitute) is probably'
        command = 'The s c.*d'
        result = sed.match_string(string, command, flags=flags)
        assert result == expected


class TestSedSearch:
    def common_assertion(self, result, control_seq):
        assert len(result) == len(control_seq)
        assert len(set(result).symmetric_difference(set(control_seq))) == 0

    @pytest.mark.parametrize(
        'processable, command, flags, control_seq',
        [
            (
                [
                    'The',
                    's command',
                    'as',
                    'in',
                    'substitute',
                    'is',
                    'probably',
                    'the',
                    'most',
                    'important',
                    'in',
                    'sed',
                    'and',
                    'has',
                    'a lot',
                    'of',
                    'different',
                    'options',
                ],
                r'^\w{3}$',
                None,
                ['The', 'the', 'sed', 'and', 'has'],
            ),
            (
                [
                    'The',
                    's command',
                    'as',
                    'in',
                    'substitute',
                    'is',
                    'probably',
                    'the',
                    'most',
                    'important',
                    'in',
                    'sed',
                    'and',
                    'has',
                    'a lot',
                    'of',
                    'different',
                    'options',
                ],
                r'^\w{3}$',
                {SedFlags.PRINT},
                [
                    'The',
                    'the',
                    'sed',
                    'and',
                    'has',
                    'The',
                    's command',
                    'as',
                    'in',
                    'substitute',
                    'is',
                    'probably',
                    'the',
                    'most',
                    'important',
                    'in',
                    'sed',
                    'and',
                    'has',
                    'a lot',
                    'of',
                    'different',
                    'options',
                ],
            ),
            (
                [
                    'The',
                    's command',
                    'as',
                    'in',
                    'substitute',
                    'is',
                    'probably',
                    'the',
                    'most',
                    'important',
                    'in',
                    'sed',
                    'and',
                    'has',
                    'a lot',
                    'of',
                    'different',
                    'options',
                ],
                r'^\w{3}$',
                {SedFlags.DELETE},
                [
                    's command',
                    'as',
                    'in',
                    'substitute',
                    'is',
                    'probably',
                    'most',
                    'important',
                    'in',
                    'a lot',
                    'of',
                    'different',
                    'options',
                ],
            ),
        ],
    )
    def test_search_on_iter_string_command(self, processable, command, flags, control_seq):
        result = list(sed.search(processable, command, flags))
        self.common_assertion(result, control_seq)

    @pytest.mark.parametrize(
        'processable, command, control_seq',
        [
            (
                [
                    'The',
                    's command',
                    'as',
                    'in',
                    'substitute',
                    'is',
                    'probably',
                    'the',
                    'most',
                    'important',
                    'in',
                    'sed',
                    'and',
                    'has',
                    'a lot',
                    'of',
                    'different',
                    'options',
                ],
                lambda l: len(l) == 3,
                ['The', 'the', 'sed', 'and', 'has'],
            )
        ],
    )
    def test_search_on_iter_callable_command(self, processable, command, control_seq):
        result = list(sed.search(processable, command))
        self.common_assertion(result, control_seq)

    @pytest.mark.parametrize(
        'processable, command, control_seq',
        [
            (
                [
                    'The',
                    's command',
                    'as',
                    'in',
                    'substitute',
                    'is',
                    'probably',
                    'the',
                    'most',
                    'important',
                    'in',
                    'sed',
                    'and',
                    'has',
                    'a lot',
                    'of',
                    'different',
                    'options',
                ],
                [r'^\w{3}$', r'^\w{2}$'],
                ['The', 'as', 'in', 'is', 'the', 'is', 'sed', 'and', 'has', 'of'],
            )
        ],
    )
    def test_search_on_iter_iterable_string_command(self, processable, command, control_seq):
        result = list(sed.search(processable, command))
        self.common_assertion(result, control_seq)

    @pytest.mark.parametrize(
        'processable, command, control_seq',
        [
            (
                [
                    'The',
                    's command',
                    'as',
                    'in',
                    'substitute',
                    'is',
                    'probably',
                    'the',
                    'most',
                    'important',
                    'in',
                    'sed',
                    'and',
                    'has',
                    'a lot',
                    'of',
                    'different',
                    'options',
                ],
                [lambda l: len(l) == 3, lambda l: len(l) == 2],
                ['The', 'as', 'in', 'is', 'the', 'is', 'sed', 'and', 'has', 'of'],
            )
        ],
    )
    def test_search_on_iter_iterable_callable_command(self, processable, command, control_seq):
        result = list(sed.search(processable, command))
        self.common_assertion(result, control_seq)
