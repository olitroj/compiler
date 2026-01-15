from shared.tree import Tree
from shared.tok import TokenType, Token
from shared.grammer import Symbol
from syntax.grammer import N

'''
    Checks whether a given [parse_tree] follows all semantic rules.
    Returns True if it does, False if it doesn't
'''
def check_semantics(parse_tree: Tree) -> bool:
    declared_symbols = {
        Token(TokenType.ID, "input"): True,
        Token(TokenType.ID, "output"): True
    } # input and output are system functions, so they are always declared

    return _traverse_tree(parse_tree, False, declared_symbols, 0)

'''
    Recurseivly traverses the [node] of the parse tree, does semantic checks and tree restructuring.
    [post_order] flag determines whether the tree is traversed post-order or pre-order (starting from the [node]).

    Returns True/False when the node passes/fails the semantic checks.
'''
def _traverse_tree(node: Tree, post_order: bool, declared_symbols: dict[Symbol], precedence_offset: int) -> bool:
    children = node.nodes

    if post_order:
        # Post-order traversal when inside of expressions
        for child in children:
            result = _traverse_tree(child, True, declared_symbols, precedence_offset)
            if result is None:
                return None
            else:
                precedence_offset = result

        if node.symbol.type == TokenType.OPEN_BRACE:
            precedence_offset += 10
        elif node.symbol.type == TokenType.CLOSE_BRACE:
            precedence_offset -= 10

        _build_ast(node, precedence_offset)
        if not _sem(node, declared_symbols):
            return None
        else:
            return precedence_offset

    else:
        # Pre-order traversal when outside of expressions
        if not _sem(node, declared_symbols):
            return False

        # Traverses children (starts post-order traversal if it enters an expression)
        for child in children:
            if child.symbol.type == N.EXPRESSION:
                if _traverse_tree(child, True, declared_symbols, precedence_offset) is None:
                    return False
            else:
                if _traverse_tree(child, False, declared_symbols, precedence_offset) is None:
                    return False
        return True

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


# TODO Write the ast function, figure out how to deal with unary and binary minus
def _build_ast(node: Tree, precedence_offset: int):
    if isinstance(node.symbol, Token) and node.symbol.precedence is not None:
        node.symbol.precedence += precedence_offset

    children = node.nodes

    for i in range(len(children)):
        child = children[i]
        grandchildren = children[i].nodes

        if len(grandchildren) == 1 and child.symbol.type in N:
            children[i] = grandchildren[0]

        if not grandchildren:
            continue

        lowest_precedence = 1000
        operator = None
        for grandchild in grandchildren:
            grand_symbol = grandchild.symbol

            if isinstance(grand_symbol, Token):
                precedence = grand_symbol.precedence
                if precedence is None:
                    continue

                if lowest_precedence > precedence:
                    lowest_precedence = precedence
                    operator = grandchild

        if operator is not None:
            for j, g in enumerate(grandchildren):
                if g != operator and g.symbol.type != TokenType.OPEN_BRACE and g.symbol.type != TokenType.CLOSE_BRACE:
                    operator.nodes.insert(j, g)
            children[i] = operator

    # Rotation