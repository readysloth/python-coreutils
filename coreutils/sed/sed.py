import functools
import itertools
import pathlib
import re
from types import FunctionType
from typing import Callable, FrozenSet, Iterable, List, Optional, Tuple, Union

import coreutils.sed.utils as utils
from coreutils.sed import SedException, SedFlags

Processor = Callable[[str], bool]
Processable = Union[str, Iterable[str], pathlib.Path, Iterable[pathlib.Path]]
Commands = Union[str, Iterable[str], Processor, Iterable[Processor]]
Flags = FrozenSet[SedFlags]

SubstituitionProcessor = Union[Tuple[str, str], Tuple[str, Callable[[str], str]]]
SubstitutionCommands = Union[SubstituitionProcessor, Iterable[SubstituitionProcessor]]


def _cast_commands_to_processors(
    commands: Union[Commands, SubstitutionCommands], flags: Flags, action: str = 'search'
) -> Iterable[Processor]:
    def _compile_regex_search(pattern: str) -> Processor:
        """
        Functon compiles regular expression and returns search
        function.
        """
        regex = re.compile(pattern, flags=re.IGNORECASE if SedFlags.INSENSITIVE in flags else 0)
        return regex.search  # type: ignore

    def _compile_regex_substitute(pattern: str, repl: Union[str, Callable[[str], str]]) -> Processor:
        """
        Functon compiles regular expression and returns substitute
        function. Substitute function repl argument can be string or function.
        """
        regex = re.compile(pattern, flags=re.IGNORECASE if SedFlags.INSENSITIVE in flags else 0)
        if SedFlags.GLOBAL in flags:
            return functools.partial(regex.subn, repl=repl)  # type: ignore
        return functools.partial(regex.subn, repl=repl, count=1)  # type: ignore

    if action == 'search' and isinstance(commands, FunctionType):
        return [commands]

    if action == 'search':
        if isinstance(commands, str):
            return [_compile_regex_search(pattern=commands)]
        return [_compile_regex_search(pattern=command) if isinstance(command, str) else command for command in commands]
    elif action == 'substitution':
        if isinstance(commands, tuple):
            return [_compile_regex_substitute(pattern=commands[0], repl=commands[1])]
        return [_compile_regex_substitute(pattern=command[0], repl=commands[1]) for command in commands]


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

def _check_flags(flags: Flags):
    if flags and SedFlags.DELETE in flags and SedFlags.PRINT in flags:
        raise SedException(flags, 'SedFlags.DELETE and SedFlags.PRINT cannot be used simultaneously')

def substitute(
    processable: Processable, commands: SubstitutionCommands, flags: Flags
) -> Union[Iterable[str], None]:  # pylint: disable=unused-argument
    """
    Print flag doubles successfull substitution
    """
    def make_substitutions_on_line(line: str, processors) -> str:
        substituted_line = line
        for processor in processors:
            substituted_line = processor(string=substituted_line)
        return substituted_line


    flags = frozenset(flags or set())
    processors = _cast_commands_to_processors(commands, flags=flags, action='substitution')
    lines = None

    processable = list(processable)
    if SedFlags.INPLACE in flags:
        file_to_lines = { }
        processing_files = isinstance(processable[0], pathlib.Path)
        if processing_files:
            for proc_able in processable:
                if not isinstance(proc_able, pathlib.Path):
                    raise SedException(processable, "If {}'s supplied as processable, no other types allowed between them".format(pathlib.Path))

                lines = _aggregate_processable_lines(proc_able)
                file_to_lines[proc_able] = []
                for line in lines:
                    substituted_line = make_substitutions_on_line(line, processors)
                    if SedFlags.PRINT in flags and substituted_line[1]:
                        file_to_lines[proc_able].append(substituted_line[0])
                    file_to_lines[proc_able].append(substituted_line[0])

            for file in file_to_lines:
                with open(file.resolve, 'w') as f:
                    f.writelines(file_to_lines[file])
        else:
            raise SedException(None, "Inplace substitution on types other than files is not implemented")

        return

    lines = _aggregate_processable_lines(processable)

    _check_flags(flags)

    for line in lines:
        substituted_line = make_substitutions_on_line(line, processors)
        if SedFlags.PRINT in flags and substituted_line[1]:
            yield substituted_line[0]
        yield substituted_line[0]

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

    _check_flags(flags)

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
    /i'm A\\/little paTtErN/Ip
    """
    command_parse_match = re.match(r'^/(?P<pattern>.*)/(?P<flags>[^/]*)$', command)
    pattern = command_parse_match.group('pattern')
    flags = {utils.FLAGS_MAP[sf] for sf in command_parse_match.group('flags')}
    return search(processable, pattern, flags)

def sed_substitute(command: str, processable: Processable) -> Iterable[str]:
    """
    s@i'm a li[t]{2}le pattern@now i'm substituted@g
    """
    def verify_separator():
        generic_solve = 'Use unique separator.'
        separator_error = None
        if separator in pattern:
            separator_error = 'Separator used in pattern.'
        if separator in substitution:
            separator_error = 'Separator used in substitution string.'
        if separator in str_flags:
            separator_error = 'Separator used in flags.'

        if separator_error:
            raise SedException(command, '{} {}'.format(separator_error, generic_solve))

    command_parse_match = re.match(r'^s(?P<separator>.)(?P<pattern>.*)(?P=separator)(?P<substitution>.*)(?P=separator)(?P<flags>.*)$', command)
    pattern = command_parse_match.group('pattern')
    separator = command_parse_match.group('separator')
    substitution = command_parse_match.group('substitution')
    str_flags = command_parse_match.group('flags')
    verify_separator()

    flags = {utils.FLAGS_MAP[sf] for sf in str_flags}

    return substitute(processable, (pattern, substitution), flags)
