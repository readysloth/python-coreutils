import os
import sys
import pathlib

import coreutils.sed.sed as sed

import pytest

class TestSedMisc:
    @pytest.mark.parametrize('line, command, sentiment',
                        [
                            (
                                'The s command (as in substitute) is probably',
                                'The s c.*d',
                                True
                             ),
                            (
                                'The s command (as in substitute) is probably',
                                'The s as in sub',
                                False
                             ),
                            (
                                'The s command (as in substitute) is probably',
                                lambda l: 'substitute' in l,
                                True
                             ),
                            (
                                'The s command (as in substitute) is probably',
                                lambda l: 'dog' in l,
                                False
                             ),
                        ])
    def test_match_line(self, line, command, sentiment):
        result = sed.match_line(line, command)
        assert result == sentiment


class TestSedSearch:
    def common_assertion(self, result, control_seq):
        assert len(result) == len(control_seq)
        assert len(set(result).symmetric_difference(set(control_seq))) == 0

    @pytest.mark.parametrize('processable, command, control_seq',
                        [
                            (
                                ['The', 's command', 'as', 'in', 'substitute', 'is',
                                 'probably', 'the', 'most', 'important', 'in', 'sed',
                                 'and', 'has', 'a lot', 'of', 'different', 'options'],
                                r'^\w{3}$',
                                ['The', 'the', 'sed', 'and', 'has']
                             )
                        ])
    def test_search_on_iter_string_command(self, processable, command, control_seq):
        result = list(sed.search(processable, command))
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

