from nterm import NTermType
from tok import TokenType

class GrammerRule:
    def __init__(self, symbol : NTermType, result : list[NTermType | TokenType]) -> None:
        self.symbol = symbol
        self.result = result

    def __str__(self) -> str:
        return f"{self.symbol.name} -> {' '.join(r.name for r in self.result)}"
    
    def __eq__(self, other : GrammerRule) -> bool:
        return self.symbol == other.symbol and self.result == other.result