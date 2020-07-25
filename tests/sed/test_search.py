import pathlib
import tempfile

import pytest

from coreutils import sed
from coreutils.sed import SedException, SedFlags


def _assert_common(result, expected):
    assert len(result) == len(expected)
    assert len(set(result).symmetric_difference(set(expected))) == 0


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
def test_search_on_iter_string_command(processable, command, flags, control_seq):
    result = list(sed.search(processable, command, flags))
    _assert_common(result, control_seq)


@pytest.mark.parametrize('processable, command, flags', [(['a'], 'b', {SedFlags.DELETE, SedFlags.PRINT})])
def test_search_flags_error(processable, command, flags):
    with pytest.raises(SedException):
        list(sed.search(processable, command, flags))


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
def test_search_on_iter_callable_command(processable, command, control_seq):
    result = list(sed.search(processable, command))
    _assert_common(result, control_seq)


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
def test_search_on_iter_iterable_string_command(processable, command, control_seq):
    result = list(sed.search(processable, command))
    _assert_common(result, control_seq)


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
def test_search_on_iter_iterable_callable_command(processable, command, control_seq):
    result = list(sed.search(processable, command))
    _assert_common(result, control_seq)


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
def test_search_on_file(processable, command, control_seq):
    lines_for_first_file = processable[::2]
    lines_for_second_file = processable[1::2]
    with tempfile.NamedTemporaryFile() as first:
        with tempfile.NamedTemporaryFile() as second:
            first.write('\n'.join(lines_for_first_file).encode())
            second.write('\n'.join(lines_for_second_file).encode())
            first.flush()
            second.flush()
            result = list(sed.search([pathlib.Path(first.name), pathlib.Path(second.name)], command))
    _assert_common(result, control_seq)
