from shared.grammer import SymbolType, Symbol, GrammerRule as GR
from shared.tok import Token, TokenType as T
from syntax.astree import AST

'''
    All non-terminal symbols types in the grammer.
'''
class N(SymbolType):
    FILE = 1
    STATEMENT = 2
    EXPRESSION = 3
    ELSE_CLAUSE = 5

    NEXT_STATEMENT = 6
    NEXT_EXPRESSION = 7

    def __init__(self, val):
        super().__init__(val, False)

'''
    All grammer rules in the language.
    It is a LL(2) grammer, so no left-recursion, and peeking one place forward in any rule is enough to know if that rule applies.
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
    # TODO : Operator rules, with precedence
    GR(N.EXPRESSION, [T.LITERAL]),
    GR(N.EXPRESSION, [T.ID]),
    GR(N.EXPRESSION, [T.OPEN_BRACE, N.EXPRESSION, T.CLOSE_BRACE])
]


'''
    An LL(2) parsing function for analysing the syntactic structure of a sequence of tokens.

    Top down, so left-recursive rules don't work.
    Doesn't use recursive descent, peeking one space forward is enough to determine if the rule fits (hence LL(2)).

    Returns a complete abstract syntax tree representing the syntax,
    or None if the sequence of tokens doesn't follow the grammer.
'''
def parse(tokens : list[Token]) -> AST | None:
    tree = AST(Symbol(N.FILE))
    if _build_tree(tree, tokens, 0) == None:
        print("Fail")
    else:
        print(tree)

'''
    Recursive function for building an AST from a sequence of tokens.
    Returns None if non successful.
'''
def _build_tree(tree : AST, tokens : list[Token], t_idx : int):
    # Go through all of the rules, check only the ones with a matching nterm
    for rule in grammer:
        if rule.nterm_type != tree.symbol.type:
            continue

        result = rule.result

        # If it reaches an epsilon rule, return t_idx without incrementing
        # TODO : Make EPLISON added to tree
        if result == None:
            return t_idx
        
        # If first and second terminal don't match, the rule doesn't fit, try the next one
        if len(result) > 1 and result[1] in T and result[1] != tokens[t_idx+1].type:
            continue
        if result[0] in T and result[0] != tokens[t_idx].type:
            continue
        # If it is a non-terminal, but there are no tokens left, try the next one (potentially epsilon)
        if result[0] in N and t_idx == len(tokens):
            continue

        # If the rule fits
        for rule_sym_type in result:
            # Add terminal symbol to tree if it matches with the rule, increment t_idx
            if rule_sym_type in T and rule_sym_type == tokens[t_idx].type:
                tree.nodes.append(AST(tokens[t_idx]))
                t_idx += 1

            # Add non-terminal symbol to tree, then recursivly expand it into non-terminals
            # If it fails to expand, return None
            elif rule_sym_type in N:
                tree.nodes.append(AST(Symbol(rule_sym_type)))
                t_idx = _build_tree(tree.nodes[-1], tokens, t_idx)
                if t_idx == None:
                    return None
                
            else:
                return None   
        return t_idx