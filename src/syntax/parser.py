from shared.grammer import SymbolType, Symbol, GrammerRule as GR
from shared.tok import Token, TokenType as T
from syntax.astree import AST

'''
    All non-terminal symbols types in the grammer.
'''
class N(SymbolType):
    FILE = 0
    STATEMENT = 2
    EXPRESSION = 3
    ELSE_CLAUSE = 5

    NEXT_STATEMENT = 6
    NEXT_EXPRESSION = 7

    NEXT_DIFF = 9
    SUM = 10
    NEXT_SUM = 11
    OR = 12
    NEXT_OR = 13

    def __init__(self, val):
        super().__init__(val, False)

'''
    All grammer rules in the language.
    It is a LL(2) grammer, so no left-recursion, and all production rules must have the first two produced symbols be unambiguous
'''
grammer = [
    # File
    GR(N.FILE, [N.STATEMENT, N.NEXT_STATEMENT]),

    # Statements
    GR(N.STATEMENT, [T.VAR, T.ID, T.ASSIGN, N.EXPRESSION, T.SEMICOLON]),            # Declaration + Assignment
    GR(N.STATEMENT, [T.ID, T.ASSIGN, N.EXPRESSION, T.SEMICOLON]),                   # Assignment
    GR(N.STATEMENT, [T.IF, N.EXPRESSION, N.STATEMENT, N.ELSE_CLAUSE]),              # Flow
    GR(N.ELSE_CLAUSE, [T.ELSE, N.STATEMENT]),
    GR(N.ELSE_CLAUSE, None),
    GR(N.STATEMENT, [T.WHILE, N.EXPRESSION, N.STATEMENT]),                          # Loop
    GR(N.STATEMENT, [T.DO, N.STATEMENT, T.WHILE, N.EXPRESSION, T.SEMICOLON]),
    GR(N.STATEMENT, [T.ID, T.OPEN_BRACE, N.EXPRESSION, N.NEXT_EXPRESSION]),         # Call
    GR(N.NEXT_EXPRESSION, [T.COMMA, N.EXPRESSION, N.NEXT_EXPRESSION]),
    GR(N.NEXT_EXPRESSION, None),
    GR(N.STATEMENT, [T.OPEN_CURLY, N.STATEMENT, N.NEXT_STATEMENT, T.CLOSE_CURLY]),  # Group
    GR(N.NEXT_STATEMENT, [N.STATEMENT, N.NEXT_STATEMENT]),
    GR(N.NEXT_STATEMENT, None),
    
    # Expressions
    # TODO : Add all operators with correct precedence levels
    GR(N.EXPRESSION, [N.OR, N.NEXT_DIFF]),
    GR(N.OR, [N.SUM, N.NEXT_OR]),
    GR(N.SUM, [T.ID, N.NEXT_SUM]),
    GR(N.SUM, [T.LITERAL, N.NEXT_SUM]),

    GR(N.NEXT_DIFF, [T.MINUS, N.EXPRESSION]),
    GR(N.NEXT_DIFF, None),
    GR(N.NEXT_OR, [T.LOGIC_OR, N.OR]),
    GR(N.NEXT_OR, None),
    GR(N.NEXT_SUM, [T.PLUS, N.SUM]),
    GR(N.NEXT_SUM, None)
]


'''
    An LL(2) parsing function for analysing the syntactic structure of a sequence of tokens.

    Top down, so left-recursive rules don't work.
    Decides which rule fits by peeking two tokens ahead (since its LL(2))

    Returns a complete parse tree representing the syntax,
    or None if the sequence of tokens doesn't follow the grammer.
'''
def parse(tokens : list[Token]) -> AST | None:
    tree = AST(Symbol(N.FILE))
    if _build_tree(tree, tokens, 0) == None:
        print("Fail")
    else:
        print(tree)

'''
    Recursive function for building a parse tree from a sequence of tokens.
    Returns None if non successful.
'''
def _build_tree(tree : AST, tokens : list[Token], t_idx : int):
    # Go through all of the rules, check only the ones with a matching nterm
    for rule in grammer:
        if rule.nterm_type != tree.symbol.type:
            continue

        result = rule.result

        # If it reaches an epsilon rule, return t_idx without incrementing
        if result == None:
            return t_idx
        
        # If first and second terminal don't match, the rule doesn't fit, try the next one
        if len(result) > 1 and result[1] in T and result[1] != tokens[t_idx+1].type:
            continue
        if result[0] in T and result[0] != tokens[t_idx].type:
            continue
        # If it is a non-terminal, but there are no tokens left, try the next rule (potentially epsilon)
        if result[0] in N and t_idx == len(tokens):
            continue

        # If the rule fits
        for rule_sym_type in result:
            # Add terminal symbol to tree if it matches with the rule, increment t_idx
            if rule_sym_type in T and rule_sym_type == tokens[t_idx].type:
                tree.nodes.append(AST(tokens[t_idx]))
                t_idx += 1

            # Add non-terminal symbol to tree, then recursivly expand it
            # If it fails to expand, return None
            elif rule_sym_type in N:
                nterm_node = AST(Symbol(rule_sym_type))
                t_idx = _build_tree(nterm_node, tokens, t_idx)

                # TODO: Decide if this is a good idea
                # Removes non-terminal from tree if it has just one terminal child, replaces it with that child
                if len(nterm_node.nodes) == 1 and nterm_node.nodes[0].symbol.type in T:
                    tree.nodes.append(nterm_node.nodes[0])
                # Removes non-terminal from tree if it have and epsilon child
                elif len(nterm_node.nodes) != 0:
                    tree.nodes.append(nterm_node)

                if t_idx == None:
                    return None
                
            else:
                return None   
        return t_idx