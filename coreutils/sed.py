import re
import enum
import typing as t
import pathlib
import fileinput
import itertools as it
import functools as ft

from collections.abc import Iterable

Processable = t.Union[t.Iterable[str], pathlib.Path, t.Iterable[pathlib.Path]]
Processor = t.Union[str, t.Callable]

class SedException(Exception):

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

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
    I = INSENSITIVE

@ft.lru_cache(typed=True)
def match_line(line:str,
               command: Processor,
               flags: t.Optional[t.FrozenSet[SedFlags]]=None) -> bool:
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

def map_command_to_line(line: str,
                        command: t.Iterable[Processor],
                        flags: t.Optional[t.Set[SedFlags]]=None) -> bool:

    matched = False
    if isinstance(command, Iterable) and not isinstance(command, str):
        for cmd in command:
            matched = matched or match_line(line, cmd)
    else:
        matched = match_line(line, command, flags)
    return (line, matched)

def substitute(to_process: Processable,
               command: t.Union[Processor, t.Iterable[Processor]],
               flags: t.Optional[t.Set[SedFlags]]=None):
    pass

def substitute_by_command(to_process: Processable,
                          command: str,
                          flags: t.Optional[t.List[SedFlags]]=None):
    pass

def search(to_process: Processable,
           command: t.Union[Processor,
                                 t.Iterable[Processor]],
           search_flags: t.Optional[t.Set[SedFlags]]=None) -> t.Iterable[str]:
    '''
    Search takes iterable or path to file and applies regular expression (can be iterable of
    regular expressions), or predicate (can be iterable of predicates) to every string in iterable or file,
    returning iterator of filtered strings.
    Can take sed flags to modify match behaviour.
    '''

    def preprocess(for_processing: t.Iterable[str] ,
                   cmds: t.Union[Processor, t.Iterable[Processor]]) -> t.Iterable[t.Tuple[str, bool]]:
        return map(map_command_to_line,       # searching line 
                        for_processing,
                        it.repeat(cmds),
                        it.repeat(search_flags))

    def filter_out_or_double(filterable: t.Iterable[t.Tuple[str, bool]]) -> t.Iterable[str]:
        if search_flags and SedFlags.PRINT in search_flags:
            doubled_if_match = []
            for element, match in filterable:
                if match:
                    doubled_if_match.append((element, match))
                doubled_if_match.append((element, match))
            return doubled_if_match
        return filter(lambda line_tuple: line_tuple[1], filterable)    # filtering out not matched

    def process(for_processing: t.Iterable[Processable]):
        preprocessed = None
        if isinstance(command, Iterable) and not isinstance(command, str):
            commands = list(command)
            preprocessed = preprocess(for_processing, commands)
        else:
            preprocessed = preprocess(for_processing, command)

        return map(lambda match_tuple: match_tuple[0],
                   filter_out_or_double(preprocessed))

    def process_file(file: pathlib.Path):
        with open(file.resolve(), 'r') as f:
            lines = f.read().splitlines()
            return process(lines)

    if search_flags:
        search_flags = frozenset(search_flags)

    if search_flags and \
       SedFlags.DELETE in search_flags and \
       SedFlags.PRINT in search_flags:
        raise SedException(search_flags,
                           'SedFlags.DELETE and SedFlags.PRINT cannot be used simultaneously')

    if isinstance(to_process, pathlib.Path):
        return process_file(to_process)
    elif isinstance(to_process, Iterable) and isinstance(to_process[0], pathlib.Path):
        result = map(process_file, to_process)
        return list(it.chain(*result))
    else:
        to_process = list(to_process)
        return process(to_process)
