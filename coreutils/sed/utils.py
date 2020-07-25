import enum


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


class SedException(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
        super(SedException, self).__init__()
