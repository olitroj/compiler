from tok import TokenType
from nterm import NTermType
from grammer import GrammerRule

rule = GrammerRule(NTermType.STATEMENT, [TokenType.VAR, TokenType.ID, TokenType.ASSIGN, NTermType.EXPRESSION, TokenType.SEMICOLON])

print(rule)