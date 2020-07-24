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


def match_string(string: str, command: Union[str, Callable], flags: Optional[Set[SedFlags]] = None,) -> bool:
    if isinstance(command, str):
        pattern = command
        command = lambda text: re.search(
            pattern=pattern, string=text, flags=re.IGNORECASE if flags and SedFlags.INSENSITIVE else 0,
        )

    is_match = bool(command(string))
    if flags and SedFlags.DELETE in flags:
        return not is_match
    return is_match


def map_command_to_string(string: str, command, flags: Optional[Set[SedFlags]] = None,) -> Tuple[str, bool]:
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
    def preprocess(commands) -> Iterable[Tuple[str, bool]]:
        return map(
            map_command_to_string,  # searching line
            to_process,
            itertools.repeat(commands),
            itertools.repeat(search_flags),
        )

    def filter_out_or_double(filterable: Iterable[Tuple[str, bool]]):
        if search_flags and SedFlags.PRINT in search_flags:
            doubled_if_match = []
            for element, match in filterable:
                if match:
                    doubled_if_match.append((element, match))
                doubled_if_match.append((element, match))
            return doubled_if_match
        return filter(lambda line_tuple: line_tuple[1], filterable)  # filtering out not matched

    to_process = list(to_process)

    if isinstance(command, Iterable) and not isinstance(command, str):
        commands = list(command)
        preprocessed = preprocess(commands)
    else:
        preprocessed = preprocess(command)

    return map(lambda match_tuple: match_tuple[0], filter_out_or_double(preprocessed))
