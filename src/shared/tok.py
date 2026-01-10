from shared.grammer import SymbolType, Symbol

'''
    Enum class representing all tokens within the language.
    The [value] is the token's lexeme (or an integer if it doesn't have one), and the [is_terminal] flag is always True
'''
class TokenType(SymbolType):
    VAR = "var"
    ID = 0
    ASSIGN = "="
    SEMICOLON = ";"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    DO = "do"
    OPEN_BRACE = "("
    CLOSE_BRACE = ")"
    COMMA = ","
    OPEN_CURLY = "{"
    CLOSE_CURLY = "}"
    LITERAL = 1
    PLUS = "+"
    MINUS = "-"
    INCREMENT = "++"
    DECREMENT = "--"
    LOGIC_AND = "&&"
    LOGIC_OR = "||"
    LOGIC_XOR = "^^"
    LOGIC_NOT = "!"
    BIT_AND = "&"
    BIT_OR = "|"
    BIT_XOR = "^"
    BIT_NOT = "~"
    SHIFT_LEFT = "<<"
    SHIFT_RIGHT = ">>"
    LESS_THAN = "<"
    LESS_THAN_EQUALS = "<="
    GREATER_THAN = ">"
    GREATER_THAN_EQUALS = ">="
    EQUAL = "=="
    NOT_EQUAL = "!="
    EOF = 2

    def __init__(self, value):
        super().__init__(value, True)

class Token(Symbol):
    def __init__(self, type: TokenType, value = None):
        super().__init__(type, value)