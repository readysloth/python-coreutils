import functools
import itertools
import pathlib
import re
from typing import Callable, Iterable, List, Optional, Set, Tuple, Union

from coreutils.sed import SedException, SedFlags

Processable = Union[Iterable[str], pathlib.Path, Iterable[pathlib.Path]]
Processor = Union[str, Callable]


@functools.lru_cache(typed=True)
def match_string(string: str, command: Union[str, Callable], flags: Optional[Set[SedFlags]] = None) -> bool:
    if isinstance(command, str):
        pattern = command
        command = lambda text: re.search(
            pattern=pattern, string=text, flags=re.IGNORECASE if flags and SedFlags.INSENSITIVE else 0,
        )

    is_match = bool(command(string))
    if flags and SedFlags.DELETE in flags:
        return not is_match
    return is_match


def map_command_to_string(string: str, command, flags: Optional[Set[SedFlags]] = None) -> Tuple[str, bool]:
    matched = False
    if isinstance(command, Iterable) and not isinstance(command, str):
        for cmd in command:
            matched = matched or match_string(string, cmd)
    else:
        matched = match_string(string, command, flags)
    return string, matched


def substitute(
    to_process: Processable, command: Union[Processor, Iterable[Processor]], flags: Optional[Set[SedFlags]] = None,
):  # pylint: disable=unused-argument
    pass


def substitute_by_command(
    to_process: Processable, command: str, flags: Optional[List[SedFlags]] = None
):  # pylint: disable=unused-argument
    pass


def search(
    to_process: Processable,
    command: Union[Processor, Iterable[Processor]],
    search_flags: Optional[Set[SedFlags]] = None,
) -> Iterable[str]:
    """
    Search takes iterable or path to file and applies regular expression (can be iterable of
    regular expressions), or predicate (can be iterable of predicates) to every string in iterable or file,
    returning iterator of filtered strings.
    Can take sed flags to modify match behaviour.
    """

    def preprocess(
        for_processing: Iterable[str], commands: Union[Processor, Iterable[Processor]]
    ) -> Iterable[Tuple[str, bool]]:
        return map(
            map_command_to_string, for_processing, itertools.repeat(commands), itertools.repeat(search_flags)
        )  # searching line

    def filter_out_or_double(filterable: Iterable[Tuple[str, bool]]) -> Union[Iterable[str], List[Tuple[str, bool]]]:
        if search_flags and SedFlags.PRINT in search_flags:
            doubled_if_match = []
            for element, match in filterable:
                if match:
                    doubled_if_match.append((element, match))
                doubled_if_match.append((element, match))
            return doubled_if_match
        return filter(lambda line_tuple: line_tuple[1], filterable)  # filtering out not matched

    def process(for_processing: Iterable[Processable]):
        if isinstance(command, Iterable) and not isinstance(command, str):
            commands = list(command)
            preprocessed = preprocess(for_processing, commands)
        else:
            preprocessed = preprocess(for_processing, command)

        return map(lambda match_tuple: match_tuple[0], filter_out_or_double(preprocessed))

    def process_file(file: pathlib.Path):
        with open(file.resolve(), 'r') as f:
            lines = f.read().splitlines()
        return process(lines)

    if search_flags:
        search_flags = frozenset(search_flags)

    if search_flags and SedFlags.DELETE in search_flags and SedFlags.PRINT in search_flags:
        raise SedException(search_flags, 'SedFlags.DELETE and SedFlags.PRINT cannot be used simultaneously')

    if isinstance(to_process, pathlib.Path):
        return process_file(to_process)
    if isinstance(to_process, Iterable) and isinstance(to_process[0], pathlib.Path):
        result = map(process_file, to_process)
        return list(itertools.chain(*result))
    to_process = list(to_process)
    return process(to_process)
