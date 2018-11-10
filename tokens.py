import logging
import re
from enum import Enum

logger = logging.getLogger(__name__)


class Token:
    def __init__(self, string, token, line_number, column, file):
        self.string = string
        self.token = token
        self.line_number = line_number
        self.column = column
        self.file = file

    def __repr__(self):
        return "Token(string=%r, token=%r, line_number=%r, column=%r, file=%r)" % (
            self.string, self.token, self.line_number, self.column, self.file
        )


class CliveKeyword(Enum):
    TRUE = ("true")
    FALSE = "false"
    FUNCTION = "function"
    RETURN = "return"
    OPERATOR = "operator"
    ENTITY = "entity"
    IMPORT = "import"


KEYWORD_LOOKUP = {}
for keyword in CliveKeyword:
    KEYWORD_LOOKUP[keyword.value] = keyword


class BaseImaginary(Enum):
    INDENT = "indent"
    DEDENT = "dedent"


class BaseToken(Enum):
    INTEGER = ("[0-9]+")
    COLON = ":"
    COMMA = ","
    EQUALS = "="
    PLUS = "\+"
    MINUS = "-"
    AT = "@"
    TAB = "\t"
    SPACE = " "
    QUESTION = "\?"
    SEMICOLON = ";"
    OPEN_PAREN = "\("
    CLOSE_PAREN = "\)"
    NEWLINE = "\n"
    CONTINUED_NEWLINE = "\\\n"
    INLINE_COMMENT = "//.*"
    IDENTIFIER = "[a-zA-Z][a-zA-Z0-9_]*"

    def __init__(self, regex):
        logger.debug(regex)
        self.regex = re.compile(regex)

    def match(self, string, start):
        value = self.regex.match(string, start)
        return value


WHITESPACE_TOKENS = [BaseToken.SPACE, BaseToken.TAB]


def get_token(string, start):
    for parser in BaseToken:
        match = parser.match(string, start)
        if match:
            return match, parser

    # if none matched, return null and the string
    return None, None



