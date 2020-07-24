import enum
import itertools
import re
from typing import Callable, Iterable, List, Optional, Set, Tuple, Union

Processable = Union[Iterable[str], str]
Processor = Union[str, Callable]


class SedFlags(enum.Enum):
    GLOBAL = enum.auto()
    PRINT = enum.auto()
    EXECUTE = enum.auto()
    INSENSITIVE = enum.auto()
    DELETE = enum.auto()
    g = GLOBAL
    d = DELETE
    p = PRINT
    e = EXECUTE
    I = INSENSITIVE  # noqa


def match_line(
    line: str, command: Union[str, Callable], flags: Optional[Set[SedFlags]] = None,
) -> bool:
    if isinstance(command, str):
        cmd = command
        if flags and SedFlags.INSENSITIVE:
            command = lambda l: re.search(cmd, l, re.IGNORECASE)
        else:
            command = lambda l: re.search(cmd, l)
    is_match = bool(command(line))

    if flags and SedFlags.DELETE in flags:
        is_match = not is_match

    return is_match


def map_command_to_line(
    line: str, command, flags: Optional[Set[SedFlags]] = None,
) -> Tuple[str, bool]:
    matched = False
    if isinstance(command, Iterable) and not isinstance(command, str):
        for cmd in command:
            matched = matched or match_line(line, cmd)
    else:
        matched = match_line(line, command, flags)
    return (line, matched)


def substitute(
    to_process: Processable,
    command: Union[Processor, Iterable[Processor]],
    flags: Optional[Set[SedFlags]] = None,
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
    def preprocess(cmds):
        return map(
            map_command_to_line,  # searching line
            to_process,
            itertools.repeat(cmds),
            itertools.repeat(search_flags),
        )

    def filter_out_or_double(filterable):
        if search_flags and SedFlags.PRINT in search_flags:
            doubled_if_match = []
            for element, match in filterable:
                if match:
                    doubled_if_match.append((element, match))
                doubled_if_match.append((element, match))
            return doubled_if_match
        return filter(
            lambda line_tuple: line_tuple[1], filterable
        )  # filtering out not matched

    to_process = list(to_process)

    if isinstance(command, Iterable) and not isinstance(command, str):
        commands = list(command)
        preprocessed = preprocess(commands)
    else:
        preprocessed = preprocess(command)

    return map(lambda match_tuple: match_tuple[0], filter_out_or_double(preprocessed))
