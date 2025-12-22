from enum import Enum
from tok import TokenType

class NonTerminalType(Enum):
    pass

class GrammerRule:
    def __init__(self, symbol : NonTerminalType, result : list[NonTerminalType | TokenType | None]) -> None:
        self.symbol = symbol
        self.result = result

    def __str__(self) -> str:
        return f"{self.symbol.name} -> {' '.join(r.name for r in self.result)}"
    
    def __eq__(self, other : GrammerRule) -> bool:
        return self.symbol == other.symbol and self.result == other.result