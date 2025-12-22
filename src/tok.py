from enum import Enum

class TokenType(Enum):
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

class Token:
    def __init__(self, type : TokenType, value = None) -> None:
        self.type = type
        self.value = value

    def __str__(self) -> str:
        return f"{self.type.name}({self.value})"
    
    def __eq__(self, other : Token) -> bool:
        return self.type == other.type and self.value == other.value