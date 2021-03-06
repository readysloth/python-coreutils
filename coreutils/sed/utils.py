import enum


class SedFlags(enum.Enum):
    GLOBAL = enum.auto()
    PRINT = enum.auto()
    INSENSITIVE = enum.auto()
    DELETE = enum.auto()
    INPLACE = enum.auto()
    g = GLOBAL
    d = DELETE
    p = PRINT
    I = INSENSITIVE  # noqa
    i = INPLACE


FLAGS_MAP = {
    'g': SedFlags.GLOBAL,
    'd': SedFlags.DELETE,
    'p': SedFlags.PRINT,
    'I': SedFlags.INSENSITIVE,
    'i': SedFlags.INPLACE,
}


class SedException(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
        super(SedException, self).__init__()
