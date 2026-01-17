from shared.grammer import SymbolType, Symbol

'''
    Enum class representing all tokens within the language.
    The [value] is the token's lexeme (or an integer if it doesn't have one), and the [is_terminal] flag is always True
'''
class TokenType(SymbolType):
    VAR = ("var")
    ID = (0)
    ASSIGN = ("=")
    SEMICOLON = (";")
    IF = ("if")
    ELSE = ("else")
    WHILE = ("while")
    DO = ("do")
    OPEN_BRACE = ("(")
    CLOSE_BRACE = (")")
    COMMA = (",")
    OPEN_CURLY = ("{")
    CLOSE_CURLY = ("}")
    LITERAL = (1)
    PLUS = ("+", 5)
    MINUS = ("-", 5)
    INCREMENT = ("++", 7)
    DECREMENT = ("--", 7)
    LOGIC_AND = ("&&", 2)
    LOGIC_OR = ("||", 2)
    LOGIC_XOR = ("^^", 2)
    LOGIC_NOT = ("!", 6)
    BIT_AND = ("&", 3)
    BIT_OR = ("|", 3)
    BIT_XOR = ("^", 3)
    BIT_NOT = ("~", 6)
    SHIFT_LEFT = ("<<", 4)
    SHIFT_RIGHT = (">>", 4)
    LESS_THAN = ("<", 0)
    LESS_THAN_EQUALS = ("<=", 0)
    GREATER_THAN = (">", 0)
    GREATER_THAN_EQUALS = (">=", 0)
    EQUAL = ("==", 1)
    NOT_EQUAL = ("!=", 1)

    def __init__(self, value, precedence = None):
        super().__init__(value, True)
        self.precedence = precedence

class Token(Symbol):
    def __init__(self, type: TokenType, value = None):
        self.value = value
        self.precedence = type.precedence
        super().__init__(type)

    def __eq__(self, other: Symbol) -> bool:
        return self.type == other.type and self.value == other.value
    
    def __repr__(self) -> str:
        return self.type.name if self.value is None else f"{self.type.name}({repr(self.value)})"
    
    def __hash__(self):
        return hash(self.type) + hash(self.value)