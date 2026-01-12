from shared.grammer import SymbolType, GrammerRule as GR
from shared.tok import TokenType as T
from enum import auto

'''
    All non-terminal symbols types in the grammer.
'''
class N(SymbolType):
    STATEMENT = auto()
    STATEMENT_LIST = auto()
    STATEMENT_LIST_NEXT = auto()
    EXPRESSION = auto()
    EXPRESSION_LIST = auto()
    EXPRESSION_LIST_NEXT = auto()
    GROUP_LIST = auto()
    GROUP_LIST_NEXT = auto()
    ELSE_CLAUSE = auto()

    P1 = auto()
    P2 = auto()
    P3 = auto()
    P4 = auto()
    P5 = auto()
    P6 = auto()
    NEXT_P0 = auto()
    NEXT_P1 = auto()
    NEXT_P2 = auto()
    NEXT_P3 = auto()
    NEXT_P4 = auto()
    NEXT_P5 = auto()
    VALUE = auto()
    
    def __init__(self, val):
        super().__init__(val, False)

'''
    All grammer rules in the language.
        - Defines all types of statements
        - Defines expressions, with operator precedence
    It is a LL(2) grammer, thus:
        - No left-recursion (resulting in right associative operators!)
        - Production rule's first 2 symbols must be non-ambiguous
'''
grammer = [
    # Start
    GR(N.STATEMENT_LIST, [N.STATEMENT, N.STATEMENT_LIST_NEXT]),
    GR(N.STATEMENT_LIST_NEXT, [T.SEMICOLON, N.STATEMENT_LIST]),
    GR(N.STATEMENT_LIST_NEXT, [T.SEMICOLON]),

    # Statements
    GR(N.STATEMENT, [T.VAR, T.ID, T.ASSIGN, N.EXPRESSION]),                         # Declaration + Assignment
    GR(N.STATEMENT, [T.ID, T.ASSIGN, N.EXPRESSION]),                                # Assignment
    
    GR(N.STATEMENT, [T.IF, N.EXPRESSION, N.STATEMENT, N.ELSE_CLAUSE]),              # Flow
    GR(N.ELSE_CLAUSE, [T.ELSE, N.STATEMENT]),
    GR(N.ELSE_CLAUSE, None),

    GR(N.STATEMENT, [T.WHILE, N.EXPRESSION, N.STATEMENT]),                          # Loop
    GR(N.STATEMENT, [T.DO, N.STATEMENT, T.WHILE, N.EXPRESSION]),

    GR(N.STATEMENT, [T.ID, T.OPEN_BRACE, N.EXPRESSION_LIST]),                       # Call
    GR(N.EXPRESSION_LIST, [T.CLOSE_BRACE]),
    GR(N.EXPRESSION_LIST, [N.EXPRESSION, N.EXPRESSION_LIST_NEXT]),
    GR(N.EXPRESSION_LIST_NEXT, [T.CLOSE_BRACE]),
    GR(N.EXPRESSION_LIST_NEXT, [T.COMMA, N.EXPRESSION, N.EXPRESSION_LIST_NEXT]),
    
    GR(N.STATEMENT, [T.OPEN_CURLY, N.GROUP_LIST]),                                  # Group
    GR(N.GROUP_LIST, [N.STATEMENT, N.GROUP_LIST_NEXT]),
    GR(N.GROUP_LIST_NEXT, [T.SEMICOLON, T.CLOSE_CURLY]),
    GR(N.GROUP_LIST_NEXT, [T.SEMICOLON, N.GROUP_LIST]),

    GR(N.STATEMENT, [T.ID, T.INCREMENT]),                                           # Implicit incrementing/decrementing
    GR(N.STATEMENT, [T.ID, T.DECREMENT]),


    # Expressions (Precedence levels, and various operators at those levels)
    GR(N.EXPRESSION, [N.P1, N.NEXT_P0]),                                            # Precedence levels
    GR(N.P1, [N.P2, N.NEXT_P1]),
    GR(N.P2, [N.P3, N.NEXT_P2]),
    GR(N.P3, [N.P4, N.NEXT_P3]),
    GR(N.P4, [N.P5, N.NEXT_P4]),
    GR(N.P5, [N.P6, N.NEXT_P5]),

    GR(N.P6, [T.MINUS, N.VALUE]),   # Last precedence level contains prefixed unary ops
    GR(N.P6, [T.BIT_NOT, N.VALUE]),
    GR(N.P6, [T.LOGIC_NOT, N.VALUE]),
    GR(N.P6, [N.VALUE]),

    # Increment decrement with highest precedence TODO: Find a better way of doing this
    GR(N.VALUE, [T.ID, T.INCREMENT, N.NEXT_P5]),
    GR(N.VALUE, [T.LITERAL, T.INCREMENT, N.NEXT_P5]),
    GR(N.VALUE, [T.OPEN_BRACE, T.INCREMENT, N.EXPRESSION, T.CLOSE_BRACE, N.NEXT_P5]),
    GR(N.VALUE, [T.ID, T.DECREMENT, N.NEXT_P5]),
    GR(N.VALUE, [T.LITERAL, T.DECREMENT, N.NEXT_P5]),
    GR(N.VALUE, [T.OPEN_BRACE, T.DECREMENT, N.EXPRESSION, T.CLOSE_BRACE, N.NEXT_P5]),

    GR(N.VALUE, [T.ID, N.NEXT_P5]),                                                 # Values (identifier, literal, or brackets)
    GR(N.VALUE, [T.LITERAL, N.NEXT_P5]),
    GR(N.VALUE, [T.OPEN_BRACE, N.EXPRESSION, T.CLOSE_BRACE, N.NEXT_P5]),


    GR(N.NEXT_P0, [T.GREATER_THAN, N.EXPRESSION]),                                  # Operators at each precedence level
    GR(N.NEXT_P0, [T.GREATER_THAN_EQUALS, N.EXPRESSION]),
    GR(N.NEXT_P0, [T.LESS_THAN, N.EXPRESSION]),
    GR(N.NEXT_P0, [T.LESS_THAN_EQUALS, N.EXPRESSION]),
    GR(N.NEXT_P0, None),

    GR(N.NEXT_P1, [T.EQUAL, N.P1]),
    GR(N.NEXT_P1, [T.NOT_EQUAL, N.P1]),
    GR(N.NEXT_P1, None),

    GR(N.NEXT_P2, [T.LOGIC_AND, N.P2]),
    GR(N.NEXT_P2, [T.LOGIC_OR, N.P2]),
    GR(N.NEXT_P2, [T.LOGIC_XOR, N.P2]),
    GR(N.NEXT_P2, None),

    GR(N.NEXT_P3, [T.BIT_AND, N.P3]),
    GR(N.NEXT_P3, [T.BIT_OR, N.P3]),
    GR(N.NEXT_P3, [T.BIT_NOT, N.P3]),
    GR(N.NEXT_P3, None),

    GR(N.NEXT_P4, [T.SHIFT_LEFT, N.P4]),
    GR(N.NEXT_P4, [T.SHIFT_RIGHT, N.P4]),
    GR(N.NEXT_P4, None),

    GR(N.NEXT_P5, [T.PLUS, N.P5]),
    GR(N.NEXT_P5, [T.MINUS, N.P5]),
    GR(N.NEXT_P5, None),
] 