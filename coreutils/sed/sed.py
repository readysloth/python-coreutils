import re
import enum
import typing
import pathlib
import fileinput
import itertools as it

from collections.abc import Iterable

Processable = typing.Union[typing.Iterable[str], pathlib.Path]
Processor = typing.Union[str, typing.Callable]

class SubstitutionFlags(enum.Enum):
    GLOBAL = enum.auto()
    PRINT = enum.auto()
    EXECUTE = enum.auto()
    INSENSITIVE = enum.auto()
    g = GLOBAL
    p = PRINT
    e = EXECUTE
    i = INSENSITIVE

def substitute(to_process: Processable,
               command: typing.Union[Processor,
                                     typing.Iterable[Processor]]=None,
               flags: typing.List[SubstitutionFlags]=None):
    if type(command) == str:
        substitute_by_command(to_process, command, flags)
    pass

def substitute_by_command(to_process: Processable,
                          command: str,
                          flags: typing.List[SubstitutionFlags]=None):
    pass

def match_line(line:str,
               command: typing.Union[str, typing.Callable]) -> bool:
    if isinstance(command, str):
        cmd = command
        command = lambda l: re.search(cmd, l)
    return bool(command(line))

def map_command_to_line(line: str,
                        command: typing.Iterable[typing.Union[str, typing.Callable]]) -> bool:
    if isinstance(command, Iterable) and not isinstance(command, str):
        matched = False
        for cmd in command:
            matched = matched or match_line(line, cmd)
        return (line, matched)
    return (line, match_line(line, command))

def search(to_process: Processable,
           command: typing.Union[Processor,
                                 typing.Iterable[Processor]]) -> typing.Iterable[str]:
            
    if isinstance(command, Iterable) and not isinstance(command, str):
        commands = list(command)
        return map(lambda match_tuple: match_tuple[0],
                        filter(lambda line_tuple: line_tuple[1],
                               map(map_command_to_line, to_process,
                                   it.cycle([commands]))))

    return map(lambda match_tuple: match_tuple[0],
                        filter(lambda line_tuple: line_tuple[1],
                               zip(to_process,
                                   map(match_line, to_process,
                                       it.cycle([command])))))

