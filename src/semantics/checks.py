from shared.tree import Tree
from shared.grammer import Symbol
from shared.tok import TokenType, Token
from syntax.grammer_def import N
from math import inf

'''
    Checks [node] against all semantic rules. Returns True/False if success/fail.
'''
def _sem(node: Tree, declared_symbols: dict[Symbol]) -> bool:
    node_symbol = node.symbol
    children = node.nodes

    # Check if identifier is declared before using it
    if node_symbol.type == TokenType.ID:
        if not node_symbol in declared_symbols:
            print("Identifier used before being declared:", node_symbol)
            return False

    if node_symbol.type == N.STATEMENT:
        # Check if identifier is being declared more than once
        if children[0].symbol.type == TokenType.VAR and children[1].symbol in declared_symbols:
            print("Identifier is already declared:", children[1].symbol)
            return False
        else:
            declared_symbols[children[1].symbol] = True
    return True

'''
    Restructures a [node]'s children to convert it into an abstract syntax tree.
    Moves operator nodes with the lowest precedence upward, making them the parent node of their binary expression.
'''
def _build_ast(node: Tree, precedence_offset: int):
    # Offsets precedence if under brackets
    # Recognize unary minus, increase it's precedence from 5 to 6
    if node.symbol.type == N.P6 and node.nodes[0].symbol.type == TokenType.MINUS:
        node.nodes[0].symbol.precedence += 1
    if isinstance(node.symbol, Token) and node.symbol.precedence is not None:
        node.symbol.precedence += precedence_offset

    children = node.nodes
    for i in range(len(children)):
        grandchildren = children[i].nodes

        if not grandchildren:
            continue

        # Find operator with lowest precedence within a nodes children
        lowest_precedence = 10000000000
        operator = None
        for gchild in grandchildren:
            if isinstance(gchild.symbol, Token) and gchild.symbol.precedence is not None:
                precedence = gchild.symbol.precedence
                if lowest_precedence > precedence:
                    lowest_precedence = precedence
                    operator = gchild

        # Pushes the operator to its parent node, conserves original parent's children and positioning (left/right) of children
        # Also removes braces
        if operator is not None:
            j = 0
            for gchild in grandchildren:
                if gchild.symbol.type == TokenType.OPEN_BRACE or gchild.symbol.type == TokenType.CLOSE_BRACE:
                    continue

                val = gchild if gchild != operator else None

                if len(operator.nodes) == j:
                    operator.nodes.append(val)
                elif operator.nodes[j] is None:
                    operator.nodes[j] = val
                j += 1
            children[i] = operator

'''
    Recursivly performs left rotations on a [root] nodes child [op1]
    while [op1] has an operator child to it's right, whith equal precedence.
'''
def _left_rotations(root: Tree, op1: Tree, op1_idx: int):
    if len(op1.nodes) < 2:
        return
    
    op2 = op1.nodes[1]
    if isinstance(op1.symbol, Token) and isinstance(op2.symbol, Token) and op1.symbol.precedence == op2.symbol.precedence:
        temp = op2
        op1.nodes[1] = op2.nodes[0]
        temp.nodes[0] = op1
        root.nodes[op1_idx] = temp
        _left_rotations(root, temp, op1_idx)