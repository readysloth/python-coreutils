import functools
import itertools
import pathlib
import re
from typing import Callable, FrozenSet, Iterable, List, Optional, Union

import coreutils.sed.utils as utils
from coreutils.sed import SedException, SedFlags

Processor = Callable[[str], bool]
Processable = Union[str, Iterable[str], pathlib.Path, Iterable[pathlib.Path]]
Commands = Union[str, Iterable[str], Processor, Iterable[Processor]]
Flags = FrozenSet[SedFlags]


def _cast_commands_to_processors(commands: Commands, flags: Flags) -> Iterable[Processor]:
    def _compile_regex_search(pattern: str) -> Processor:
        regex = re.compile(pattern, flags=re.IGNORECASE if SedFlags.INSENSITIVE in flags else 0)
        return regex.search  # type: ignore

    if isinstance(commands, str):
        return [_compile_regex_search(pattern=commands)]

    if not isinstance(commands, Iterable):
        return [commands]

    return [_compile_regex_search(pattern=command) if isinstance(command, str) else command for command in commands]


def _aggregate_processable_lines(processable: Processable) -> Iterable[str]:
    def _process_file(path: pathlib.Path) -> Iterable[str]:
        return path.read_text().splitlines()

    if isinstance(processable, str):
        return [processable]

    if isinstance(processable, pathlib.Path):
        return _process_file(processable)

    lines: List[str] = []
    for process in processable:
        if isinstance(process, pathlib.Path):
            lines += _process_file(path=process)
        else:
            lines.append(process)
    return lines


@functools.lru_cache(typed=True)
def _match_line(line: str, processor: Processor, flags: Flags) -> bool:
    is_match = processor(line)
    if SedFlags.DELETE in flags:
        return not is_match
    return is_match


def _is_processors_matched(line: str, processors: Iterable[Processor], flags: Flags) -> bool:
    for processor in processors:
        if _match_line(line, processor, flags=flags):
            return True
    return False


def substitute(
    processable: Processable, processors: Iterable[Processor], flags: Flags
):  # pylint: disable=unused-argument
    pass


def search(processable: Processable, commands: Commands, flags: Optional[Flags] = None) -> Iterable[str]:
    """
    Search takes iterable or path to file and applies regular expression (can be iterable of
    regular expressions), or predicate (can be iterable of predicates) to every string in iterable or file,
    returning iterator of filtered strings.
    Can take sed flags to modify match behaviour.
    """
    flags = frozenset(flags or set())
    processors = _cast_commands_to_processors(commands, flags=flags)
    lines = _aggregate_processable_lines(processable)

    if flags and SedFlags.DELETE in flags and SedFlags.PRINT in flags:
        raise SedException(flags, 'SedFlags.DELETE and SedFlags.PRINT cannot be used simultaneously')

    match_lines, filter_lines = itertools.tee(lines, 2)
    is_matched_strings = (
        _is_processors_matched(line=text, processors=prcs, flags=flags)
        for text, prcs in zip(match_lines, itertools.repeat(processors))  # noqa
    )

    if SedFlags.PRINT not in flags:
        return [line for line, is_matched in zip(filter_lines, is_matched_strings) if is_matched]

    matches = []
    for line, is_matched in zip(filter_lines, is_matched_strings):
        if is_matched:
            matches.append(line)
        matches.append(line)
    return matches

def sed_search(command: str, processable: Processable) -> Iterable[str]:
    """
    /i'm A\/little paTtErN/Ip
    """
    command_parse_match = re.match(r"^/(?P<pattern>.*)/(?P<flags>[^/]*)$", command)
    pattern = command_parse_match.group('pattern')
    flags = { utils.FLAGS_MAP[sf] for sf in command_parse_match.group('flags')}
    return search(processable, pattern, flags)
