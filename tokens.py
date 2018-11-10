import logging
import re
from enum import Enum

logger = logging.getLogger(__name__)


class TokenParser:
    def __init__(self, name, regex):
        self.name = name
        self.value = regex
        self.regex = re.compile(regex)

    def match(self, string, start):
        value = self.regex.match(string, start)
        return value

    def __eq__(self, other):
        return hasattr(other, "name") and other.name == self.name

    def __repr__(self):
        return "LegalToken(name=%r, regex=%r)" % (self.name, self.value)

    def matches(self, tok_list, index):
        # returns the number of items matched from the index in the list
        if tok_list[index].token == self:
            return 1
        else:
            return 0

INDENT_TOKEN = TokenParser("$INDENT", "$INDENT")
DEDENT_TOKEN = TokenParser("$DEDENT", "$DEDENT")

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


def split_tokens(tokens, split):
    to_return = []
    current = []
    for token in tokens:
        if token.token == split:
            to_return.append(current)
            current = []
        else:
            current.append(token)
    to_return.append(current)  # add the final one
    return to_return


class CliveKeyword(Enum):
    TRUE = "true"
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
    INTEGER = "[0-9]+"
    STRING = "\"[^\"]*\""
    DIRECTIVE = "\$[a-zA-Z][a-zA-Z0-9_]*"
    KEYWORD = "@[a-zA-Z][a-zA-Z0-9_]*"
    IDENTIFIER = "[a-zA-Z][a-zA-Z0-9_]*"
    INLINE_COMMENT = "#[^\n]*"
    COLON = ":"
    COMMA = ","
    EQUALS = "="
    PLUS = "\+"
    MINUS = "-"
    AT = "@"
    ROOT = "\$"
    TAB = "\t"
    SPACE = " "
    NEWLINE = "\n"
    CONTINUED_NEWLINE = "\\\n"

    def __init__(self, regex):
        logger.debug(regex)
        self.regex = re.compile(regex)

    def match(self, string, start):
        value = self.regex.match(string, start)
        return value


WHITESPACE_TOKENS = [BaseToken.SPACE, BaseToken.TAB]
STRIP_TOKENS = [BaseToken.SPACE, BaseToken.TAB, BaseToken.INLINE_COMMENT, BaseToken.CONTINUED_NEWLINE]
WHITESPACE_SKIP = [BaseToken.NEWLINE, BaseToken.INLINE_COMMENT]


def get_token(string, start, tokens=BaseToken):
    for parser in tokens:
        match = parser.match(string, start)
        if match:
            return match, parser

    # if none matched, return null and the string
    return None, None



