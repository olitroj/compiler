from shared.tree import Tree
from shared.tok import Token, TokenType
from semantics.traversal import _pre_order

'''
    Checks whether a given [parse_tree] follows all semantic rules, and converts it into an AST.
    Returns True if it does, False if it doesn't
'''
def check_semantics(parse_tree: Tree) -> bool:
    declared_symbols = {
        Token(TokenType.ID, "input"): True,
        Token(TokenType.ID, "output"): True
    } # input and output are system functions, so they are always declared

    return _pre_order(parse_tree, declared_symbols, 0)