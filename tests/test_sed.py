import os
import sys
import pathlib

import coreutils.sed.sed as sed

import pytest

class TestSedMisc:
    @pytest.mark.parametrize('line, command, flags, sentiment',
                        [
                            (
                                'The s command (as in substitute) is probably',
                                'The s c.*d',
                                None,
                                True
                             ),
                            (
                                'The s command (as in substitute) is probably',
                                'The s c.*d',
                                {sed.SedFlags.DELETE},
                                False
                             ),
                            (
                                'The s command (as in substitute) is probably',
                                'the',
                                {sed.SedFlags.I},
                                True
                             ),
                            (
                                'The s command (as in substitute) is probably',
                                'The s as in sub',
                                None,
                                False
                             ),
                            (
                                'The s command (as in substitute) is probably',
                                lambda l: 'substitute' in l,
                                None,
                                True
                             ),
                            (
                                'The s command (as in substitute) is probably',
                                lambda l: 'substitute' in l,
                                {sed.SedFlags.DELETE},
                                False
                             ),
                            (
                                'The s command (as in substitute) is probably',
                                lambda l: 'dog' in l,
                                None,
                                False
                             ),
                        ])
    def test_match_line(self, line, command, flags, sentiment):
        result = sed.match_line(line, command, flags)
        assert result == sentiment


class TestSedSearch:
    def common_assertion(self, result, control_seq):
        assert len(result) == len(control_seq)
        assert len(set(result).symmetric_difference(set(control_seq))) == 0

    @pytest.mark.parametrize('processable, command, flags, control_seq',
                        [
                            (
                                ['The', 's command', 'as', 'in', 'substitute', 'is',
                                 'probably', 'the', 'most', 'important', 'in', 'sed',
                                 'and', 'has', 'a lot', 'of', 'different', 'options'],
                                r'^\w{3}$',
                                None,
                                ['The', 'the', 'sed', 'and', 'has']
                             ),
                            (
                                ['The', 's command', 'as', 'in', 'substitute', 'is',
                                 'probably', 'the', 'most', 'important', 'in', 'sed',
                                 'and', 'has', 'a lot', 'of', 'different', 'options'],
                                r'^\w{3}$',
                                {sed.SedFlags.DELETE},
                                ['s command', 'as', 'in', 'substitute', 'is',
                                 'probably', 'most', 'important', 'in',
                                 'a lot', 'of', 'different', 'options'],
                             )
                        ])
    def test_search_on_iter_string_command(self, processable, command, flags, control_seq):
        result = list(sed.search(processable, command, flags))
        self.common_assertion(result, control_seq)


    @pytest.mark.parametrize('processable, command, control_seq',
                        [
                            (
                                ['The', 's command', 'as', 'in', 'substitute', 'is',
                                 'probably', 'the', 'most', 'important', 'in', 'sed',
                                 'and', 'has', 'a lot', 'of', 'different', 'options'],
                                lambda l: len(l) == 3,
                                ['The', 'the', 'sed', 'and', 'has']
                             )
                        ])
    def test_search_on_iter_callable_command(self, processable, command, control_seq):
        result = list(sed.search(processable, command))
        self.common_assertion(result, control_seq)


    @pytest.mark.parametrize('processable, command, control_seq',
                        [
                            (
                                ['The', 's command', 'as', 'in', 'substitute', 'is',
                                 'probably', 'the', 'most', 'important', 'in', 'sed',
                                 'and', 'has', 'a lot', 'of', 'different', 'options'],
                                [r'^\w{3}$', r'^\w{2}$'],
                                ['The', 'as', 'in', 'is', 'the', 'is',
                                 'sed', 'and', 'has', 'of']
                             )
                        ])
    def test_search_on_iter_iterable_string_command(self, processable, command, control_seq):
        result = list(sed.search(processable, command))
        self.common_assertion(result, control_seq)

    
    @pytest.mark.parametrize('processable, command, control_seq',
                        [
                            (
                                ['The', 's command', 'as', 'in', 'substitute', 'is',
                                 'probably', 'the', 'most', 'important', 'in', 'sed',
                                 'and', 'has', 'a lot', 'of', 'different', 'options'],
                                [lambda l: len(l) == 3, lambda l: len(l) == 2],
                                ['The', 'as', 'in', 'is', 'the', 'is',
                                 'sed', 'and', 'has', 'of']
                             )
                        ])
    def test_search_on_iter_iterable_callable_command(self, processable, command, control_seq):
        result = list(sed.search(processable, command))
        self.common_assertion(result, control_seq)

