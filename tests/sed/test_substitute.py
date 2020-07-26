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
