import logging

from tokens import WHITESPACE_TOKENS, CliveToken, CliveImaginary, Token, KEYWORD_LOOKUP, get_token

logger = logging.getLogger(__name__)


def tokenize(string, line_number=1, file_name=None):
    tokens = []
    start = 0
    while start < len(string):
        match, token = get_token(string, start)
        if match:
            # get the string value of the token
            end = match.end()
            value = string[start:end]

            # if the token is an identifier, check if it's a keyword
            if token is CliveToken.IDENTIFIER:
                new_token = KEYWORD_LOOKUP.get(value.lower(), None)
                # if it's a keyword set the identifier to it
                if new_token:
                    token = new_token
            tokens.append(Token(value, token, line_number, start, file_name))
            start = end
        else:
            logger.debug("tokens: %s" % tokens)
            # print things pretty like
            raise SyntaxError("invalid token after %s" % tokens[-1])

    return tokens


class FileTokenizer:
    def __init__(self, file):
        self.file = file
        self.file_name = file.name
        self.file_tokens = []
        self.previous_indentation = 0
        self.indentations = []

    def get_current_indentation(self, tokens):
        """
        Get the level of indentation for the current line of tokens. Needs the previous for the value of ignored lines
        """

        current_indentation = 0
        for token in tokens:
            if token.token in WHITESPACE_TOKENS:
                current_indentation += 1
            elif token.token in [CliveToken.NEWLINE, CliveToken.INLINE_COMMENT]:
                # if the current line is empty or just has a comment, ignore its indentation
                current_indentation = self.previous_indentation
                break
            else:
                break
        return current_indentation

    def add_indent_tokens(self, current_indentation, line_num):
        if current_indentation != self.previous_indentation:
            diff = abs(current_indentation - self.previous_indentation)
            if current_indentation > self.previous_indentation:
                self.file_tokens.append(Token(diff, CliveImaginary.INDENT, line_num, current_indentation, self.file_name))
                self.indentations.append(diff)
            else:
                # can dedent multiple times in a single line
                while diff > 0:
                    last_diff = self.indentations.pop()
                    diff -= last_diff
                    self.file_tokens.append(Token(-last_diff, CliveImaginary.DEDENT, line_num, current_indentation + diff, self.file_name))

    def tokenize_file(self):
        for line_num, line in enumerate(self.file):
            line_tokens = tokenize(line, line_num, self.file_name)

            # do whitespace handling

            # count the number of whitespace tokens in this line
            current_indentation = self.get_current_indentation(line_tokens)

            logger.debug("Previous/current indents: %s/%s" % (self.previous_indentation, current_indentation))
            # if the indentation is different, then add in indents and dedents as needed

            self.add_indent_tokens(current_indentation, line_num)

            # Once we're done with the line, swap the current
            self.previous_indentation = current_indentation

            # now that we have taken care of the whitespace-sensitive portion of the code, rip it all out
            line_tokens = list(filter(lambda x: x.token not in WHITESPACE_TOKENS, line_tokens))

            self.file_tokens += line_tokens

        # once all lines in the file have been parsed, set the current indentation to zero and do final dedents
        current_indentation = 0
        self.add_indent_tokens(current_indentation, -1)
        return self.file_tokens


