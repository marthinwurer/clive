from enum import Enum
from tokens import CliveToken, CliveKeyword

T = CliveToken
K = CliveKeyword

class CliveGrammar(Enum):
    integer_constant = ((T.INTEGER,),)
    true = ((T.TRUE,),)
    false = ((T.FALSE,),)
    ternary = ((T.ZERO,),)
    expression = (())
    function = (())
    # TODO : blank lines, comment only lines, make cfg in a file then make a parser to read it and assign it classes from a dict,
