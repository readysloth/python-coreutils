import pathlib
import tempfile

import pytest

from coreutils import sed
from coreutils.sed import SedException, SedFlags

def _assert_common(result, expected):
    assert len(result) == len(expected)
    assert len(set(result).symmetric_difference(set(expected))) == 0

@pytest.mark.parametrize(
    'processable, match, substitute, flags, control_seq',
    [
        (
            [
                '99 bottles of beer on the wall, 99 bottles of beer.',
                'Take one down and pass it around, 98 bottles of beer on the wall.',
                '98 bottles of beer on the wall, 98 bottles of beer.',
                'Take one down and pass it around, 97 bottles of beer on the wall.',
            ],
            r'9.',
            r'*Deleted*',
            None,
            [
                '*Deleted* bottles of beer on the wall, 99 bottles of beer.',
                'Take one down and pass it around, *Deleted* bottles of beer on the wall.',
                '*Deleted* bottles of beer on the wall, 98 bottles of beer.',
                'Take one down and pass it around, *Deleted* bottles of beer on the wall.',
            ],
        ),
        (
            [
                '99 bottles of beer on the wall, 99 bottles of beer.',
                'Take one down and pass it around, 98 bottles of beer on the wall.',
                '98 bottles of beer on the wall, 98 bottles of beer.',
                'Take one down and pass it around, 97 bottles of beer on the wall.',
            ],
            r'9.',
            r'*Deleted*',
            {SedFlags.GLOBAL},
            [
                '*Deleted* bottles of beer on the wall, *Deleted* bottles of beer.',
                'Take one down and pass it around, *Deleted* bottles of beer on the wall.',
                '*Deleted* bottles of beer on the wall, *Deleted* bottles of beer.',
                'Take one down and pass it around, *Deleted* bottles of beer on the wall.',
            ],
        ),
    ],
)
def test_substitute_on_string_command(processable, match, substitute, flags, control_seq):
    result = list(sed.substitute(processable, (match, substitute), flags))
    print(result)
    _assert_common(result, control_seq)

@pytest.mark.parametrize(
    'processable, match, substitute, flags, control_seq',
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
            r'^..',
            r'##',
            {SedFlags.PRINT},
            [
                '##e',
                '##command',
                '##',
                '##',
                '##bstitute',
                '##',
                '##obably',
                '##e',
                '##st',
                '##portant',
                '##',
                '##d',
                '##d',
                '##s',
                '##lot',
                '##',
                '##fferent',
                '##tions',
            ]*2,
        )
    ],
)
def test_substitute_on_file(processable, match, substitute, flags, control_seq):
    lines_for_first_file = processable[::2]
    lines_for_second_file = processable[1::2]
    with tempfile.NamedTemporaryFile(mode='w+') as first:
        with tempfile.NamedTemporaryFile(mode='w+') as second:
            first.write('\n'.join(lines_for_first_file))
            second.write('\n'.join(lines_for_second_file))
            first.flush()
            second.flush()
            result = list(sed.substitute([pathlib.Path(first.name), pathlib.Path(second.name)], (match, substitute), flags))
    _assert_common(result, control_seq)


@pytest.mark.parametrize(
    'original_seq, match, substitute, flags, control_seq',
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
            r'^..',
            r'##',
            {SedFlags.INPLACE},
            [
                '##e',
                '##command',
                '##',
                '##',
                '##bstitute',
                '##',
                '##obably',
                '##e',
                '##st',
                '##portant',
                '##',
                '##d',
                '##d',
                '##s',
                '##lot',
                '##',
                '##fferent',
                '##tions',
            ],
        )
    ],
)
def test_substitute_on_file_inplace(original_seq, match, substitute, flags, control_seq):
    lines_for_first_file = original_seq
    with tempfile.NamedTemporaryFile(mode='w+') as first:
        first.write('\n'.join(lines_for_first_file))
        first.flush()
        sed.substitute(pathlib.Path(first.name), (match, substitute), flags)
        first.seek(0)
        lines = first.readlines()
        result = list(map(str.strip, lines))
    _assert_common(result, control_seq)
