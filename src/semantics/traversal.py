from shared.tok import TokenType
from shared.tree import Tree
from shared.grammer import Symbol
from syntax.grammer_def import N

from semantics.checks import _sem, _left_rotations, _build_ast

'''
    These functions recursivly traverse the [node] of a parse tree.
    During pre-order traversal, it's checks if [node] obeys all semantic rules.

    When it reaches a EXPRESSION node, it starts traversing in post-order, pushing operator nodes to the parent of two values.
    Once it finished, it does another traversal in pre-order, performing left rotation to change right associativity to left.
    As a result, expressions are converted into abstract syntax trees.

    Returns True/False when the node passes/fails the semantic checks.
'''
def _pre_order(node: Tree, declared_symbols: dict[Symbol], precedence_offset: int) -> bool:
    # Handle None nodes (used for operator positions in AST)
    if node is None:
        return True
    
    # Semantics check
    if not _sem(node, declared_symbols):
        return False

    for i, child in enumerate(node.nodes):
        # If it reaches a None node (used to show if node has only a right child)
        if child is None:
            continue

        # Performs rotations if two operators with equal precedence are in a "right" tree
        _left_rotations(node, child, i)

        # Traverses children
        # If it reaches an expression node: 1) Post-order traversal to build AST 2) Pre-order traversal to perform rotations
        if child.symbol.type == N.EXPRESSION:
            if _post_order(child, declared_symbols, precedence_offset) is None:
                return False
            if not _pre_order(child, declared_symbols, precedence_offset):
                return False
        else:
            if not _pre_order(child, declared_symbols, precedence_offset):
                return False
            
    return True

def _post_order(node: Tree, declared_symbols: dict[Symbol], precedence_offset: int):
    # Traverses children
    for child in node.nodes:
        # Skip None nodes (used to represent operator positions in AST)
        if child is None:
            continue
            
        result = _post_order(child, declared_symbols, precedence_offset)
        if result is None:
            return None
        else:
            precedence_offset = result

    # Increments/Decrements precedence_offset
    if node.symbol.type == TokenType.OPEN_BRACE:
        precedence_offset += 10
    elif node.symbol.type == TokenType.CLOSE_BRACE:
        precedence_offset -= 10

    # Builds AST
    _build_ast(node, precedence_offset)

    return precedence_offset