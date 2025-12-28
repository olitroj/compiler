from shared.grammer import TerminalType

'''
    Enum class representing all tokens within the language, and their lexeme.
    Are terminal symbols.
'''
class TokenType(TerminalType):
    VAR = "var"
    ID = None
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
    LITERAL = None
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

'''
    Class representing a single token. Contains a type, and an optional value.
'''
class Token:
    def __init__(self, type : TokenType, value = None) -> None:
        self.type = type
        self.value = value

    def __str__(self) -> str:
        return f"{self.type.name}({self.value})"
    
    def __eq__(self, other : Token) -> bool:
        return self.type == other.type and self.value == other.value