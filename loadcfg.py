import ast
import logging
import re

from tokenizer import tokenize, FileTokenizer
from tokens import BaseToken, split_tokens, TokenParser, INDENT_TOKEN, DEDENT_TOKEN

logger = logging.getLogger(__name__)


def append_or_add(d, k, i):
    if k in d:
        d[k].append(i)
    else:
        d[k] = [i]


# rules can match any of their items, productions must match all


class Production:
    def __init__(self, items):
        self.items = items

    def matches(self, tok_list, index):
        matched = 0
        for rule in self.items:
            logger.debug("Token: %s Trying rule %s" % (tok_list[index].token.name, rule.name))
            rule_matched = rule.matches(tok_list, index + matched)
            if rule_matched == 0:
                return 0  # all rules in a production must match to be valid
            matched += rule_matched
        logger.debug("Matched!")
        return matched

    def __repr__(self):
        return "Production(%s)" % (", ".join([x.name for x in self.items]))

    def __str__(self):
        return ", ".join([x.name for x in self.items])


class Rule:
    def __init__(self, name, productions):
        self.name = name
        self.productions = productions

    def add_production(self, production):
        self.productions.append(production)

    def matches(self, tok_list, index):
        # returns the number of items matched from the index in the list
        for production in self.productions:
            logger.debug("Trying %s" % production)
            matched = production.matches(tok_list, index)
            if matched == 0:
                continue  # try the next production
            # otherwise we matched!
            return matched
        # if none were matched return 0
        return 0

    def __repr__(self):
        return "Rule(name=%r, productions=%r)" % (self.name, self.productions)


class CFG:
    def __init__(self, file_name):
        self.config_file = file_name
        self.tokens = []
        self.keywords = []
        self.rules = []
        self.directives = {}
        self.unresolved_directives = {}
        self.base_rule = None
        self.indentation = False
        self.whitespace_tokens = []
        self.whitespace_skip = []
        self.filter_out = []

        self.name_to_rule = {}
        self.name_to_production_names = {}
        self.unresolved_productions = {}  # maps rule name to its productions

    def add_token(self, rule, regex):
        name = rule.string
        value = ast.literal_eval(regex.string)  # strip off the quotes and correctly escape the value
        new_token = TokenParser(name, value)
        self.tokens.append(new_token)
        self.name_to_rule[name] = new_token

    def add_keyword(self, rule, regex):
        name = rule.string
        value = ast.literal_eval(regex.string)  # strip off the quotes and correctly escape the value
        new_keyword = TokenParser(name, value)
        self.keywords.append(new_keyword)
        self.name_to_rule[name] = new_keyword

    def add_rule(self, rule, production):
        name = rule.string
        rule_names = [x.string for x in production]
        new_rule = Rule(name, [])
        if name not in self.name_to_rule:
            self.name_to_rule[name] = new_rule
            self.unresolved_productions[name] = []
        self.unresolved_productions[name].append(rule_names)

    def add_directive(self, rule, production):
        name = rule.string
        rule_names = [x.string for x in production]
        append_or_add(self.unresolved_directives, name, rule_names)

    def load(self):
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
                    if len(production) == 1 and production[0].token == BaseToken.STRING:
                        self.add_token(rule, production[0])
                    else:
                        self.add_rule(rule, production)
                elif rule.token == BaseToken.ROOT:
                    # new parser directive
                    self.add_rule(rule, production)
                else:
                    # something went wrong with this line, error
                    logger.error("Expected keyword, directive, or identifier, got %s" % rule)
                    logger.error(line)
                    raise SyntaxError

        # parse the indent directives
        if "$INDENT" in self.unresolved_directives:
            self.indentation = True
            self.name_to_rule["$INDENT"] = INDENT_TOKEN
        if "$DEDENT" in self.unresolved_directives:
            self.indentation = True
            self.name_to_rule["$DEDENT"] = DEDENT_TOKEN

        fully_resolved = self.name_to_rule  # should be name to rule or name to test?
        unresolved = self.unresolved_productions
        # once the file has been loaded, then we can have fun putting together the productions
        for name, productions in unresolved.items():
            for production in productions:
                resolved = []
                for rule in production:
                    if rule in fully_resolved:
                        resolved.append(fully_resolved[rule])
                    else:
                        logger.error("Failed to resolve %s" % rule)
                        raise SyntaxError

                # if you make the end, then append the resolved production to our fully resolved value
                new_production = Production(resolved)
                fully_resolved[name].add_production(new_production)

        # parse the rest of the directives
        for name, productions in self.unresolved_directives.items():
            resolved = []  # resolution is out here because I just want everything
            for production in productions:
                for rule in production:
                    if rule in fully_resolved:
                        resolved.append(fully_resolved[rule])
                    else:
                        logger.error("Failed to resolve %s" % rule)
                        raise SyntaxError

            # if you make the end, then append the resolved production to our fully resolved value
            self.directives[name] = resolved

        self.whitespace_tokens = self.directives.get("$WHITESPACE", [])
        self.whitespace_skip = self.directives.get("$WHITESPACE_SKIP", [])
        self.filter_out = self.directives.get("$FILTER_OUT", [])
        self.base_rule = self.name_to_rule["$"]

    def tokenize_file(self, file_name):
        # class FileTokenizer:
        #     def __init__(self, file, indention=False, valid_tokens=BaseToken, whitespace=WHITESPACE_TOKENS,
        #                  filter_out=STRIP_TOKENS, whitespace_skip=WHITESPACE_SKIP):
        with open(file_name) as file:
            tokenizer = FileTokenizer(file, indention=True,
                                      valid_tokens=self.tokens,
                                      whitespace=self.whitespace_tokens,
                                      filter_out=self.filter_out,
                                      whitespace_skip=self.whitespace_skip)
            tokens = tokenizer.tokenize_file()
        return tokens

    def matches(self, token_list):
        index = 0
        matched = self.base_rule.matches(token_list, index)
        tokens = [x.token.name for x in token_list]
        logger.info(tokens)
        logger.info(matched)


