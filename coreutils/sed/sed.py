import re
import enum
import typing
import pathlib
import fileinput
import itertools as it

from collections.abc import Iterable

Processable = typing.Union[typing.Iterable[str], pathlib.Path]
Processor = typing.Union[str, typing.Callable]

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

def match_line(line:str,
               command: typing.Union[str,
                                     typing.Callable],
               flags: typing.Set[SedFlags]=None) -> bool:
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
                        command: typing.Iterable[typing.Union[str,
                                                              typing.Callable]],
                        flags: typing.Set[SedFlags]=None) -> bool:

    matched = False
    if isinstance(command, Iterable) and not isinstance(command, str):
        for cmd in command:
            matched = matched or match_line(line, cmd)
    else:
        matched = match_line(line, command, flags)
    return (line, matched)

def substitute(to_process: Processable,
               command: typing.Union[Processor,
                                     typing.Iterable[Processor]]=None,
               flags: typing.Set[SedFlags]=None):
    pass

def substitute_by_command(to_process: Processable,
                          command: str,
                          flags: typing.List[SedFlags]=None):
    pass

def search(to_process: Processable,
           command: typing.Union[Processor,
                                 typing.Iterable[Processor]],
           search_flags: typing.Set[SedFlags]=None) -> typing.Iterable[str]:

    to_process = list(to_process)
            
    if isinstance(command, Iterable) and not isinstance(command, str):
        commands = list(command)
        return map(lambda match_tuple: match_tuple[0],              # getting matched string
                        filter(lambda line_tuple: line_tuple[1],    # filtering out not matched
                               map(map_command_to_line,             # searching line 
                                   to_process,
                                   it.cycle([commands]),
                                   it.cycle([search_flags]))))

    return map(lambda match_tuple: match_tuple[0],                  # getting matched string
                        filter(lambda line_tuple: line_tuple[1],    # filtering out not matched
                               zip(to_process,                      # zipping with strings,
                                                                    #   because we got only bool's
                                   map(match_line,                  # filtering out not matched
                                       to_process,
                                       it.cycle([command]),
                                       it.cycle([search_flags])))))

