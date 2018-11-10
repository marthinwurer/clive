import logging

from tokenizer import FileTokenizer, tokenize
from tokens import BaseToken, STRIP_TOKENS, split_tokens

logger = logging.getLogger(__name__)


def append_or_add(d, k, i):
    if k in d:
        d[k].append(i)
    else:
        d[k] = [i]


class CFG:
    def __init__(self, file_name):
        self.config_file = file_name
        self.tokens = []
        self.keywords = []
        self.rules = []
        self.base_rule = None

        self.name_to_productions = {}
        self.token_name_to_regex = {}

    def add_token(self, rule, regex):
        pass

    def add_keyword(self, rule, regex):
        pass

    def add_rule(self, rule, production):
        pass

    def add_directive(self, rule, production):
        pass

    def parse_file(self):
        with open(self.config_file) as file:
            for line_num, line in enumerate(file):
                logger.debug("Line num: %s" % line_num)
                line_tokens = tokenize(line, line_num, self.config_file)

                # filter out the useless tokens
                line_tokens = list(filter(lambda x: x.token not in [
                    BaseToken.INLINE_COMMENT,
                    BaseToken.CONTINUED_NEWLINE,
                    BaseToken.NEWLINE,
                    BaseToken.SPACE,
                    BaseToken.TAB,
                ], line_tokens))

                logger.debug("Filtered tokens: %s" % line_tokens)


                # make sure that there's a token in the line,
                if len(line_tokens) == 0:
                    continue

                # split the line into name and production
                split = split_tokens(line_tokens, BaseToken.COLON)
                # if there are not two items, then this is a bad line
                if len(split) != 2:
                    logger.error("Expected rule and production, got %s" % len(split))
                    logger.error(line)
                    raise SyntaxError
                rule = split[0]
                if len(rule) != 1:
                    logger.error("Expected one rule got %s" % len(rule))
                    logger.error(line)
                    logger.error(rule)
                    raise SyntaxError
                rule = rule[0]

                production = split[-1]

                # keywords have a single production that is a string
                if rule.token == BaseToken.KEYWORD:
                    if len(production) != 1:
                        logger.error("Expected one production got %s" % len(production))
                        logger.error(line)
                        logger.error(production)
                        raise SyntaxError

                    item = production[0]
                    if item.token == BaseToken.STRING:
                        self.add_keyword(rule, item)
                    else:
                        logger.error("Expected a string, got %s" % item)
                        logger.error(line)
                        logger.error(production)
                        raise SyntaxError
                elif rule.token == BaseToken.DIRECTIVE:
                    # new parser directive
                    self.add_directive(rule, production)

                elif rule.token == BaseToken.IDENTIFIER:
                    # if the first item is an identifier, then it's a rule or token
                    # it's a token if the only production it has is a string
                    if len(production) == 1 and production[0] == BaseToken.STRING:
                        self.add_token(rule, production[0])
                    else:
                        self.add_rule(rule, production)
                elif rule.token == BaseToken.ROOT:
                    # new parser directive
                    self.add_directive(rule, production)
                else:
                    # something went wrong with this line, error
                    logger.error("Expected keyword, directive, or identifier, got %s" % rule)
                    logger.error(line)
                    raise SyntaxError







