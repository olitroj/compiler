from enum import Enum

'''
    Enum classes that represent a terminal or non-terminal symbol type.
    Abstract class, inherit this class to define symbol types in a grammer.
'''
class TerminalType(Enum):
    pass
class NonTerminalType(Enum):
    pass

'''
    Classes that represent terminal or non-terminal symbols.
    Abstract class, inherit this class to define symbols in a grammer.
'''
class Terminal:
    pass
class NonTerminal:
    pass

'''
    Class representing a production rule for a reguler or context-free grammer.
'''
class GrammerRule:
    def __init__(self, symbol : NonTerminalType, result : list[NonTerminalType | TerminalType] | None) -> None:
        self.symbol = symbol
        self.result = result

    def __str__(self) -> str:
        return f"{self.symbol.name} -> {' '.join(r.name for r in self.result)}"
    
    def __eq__(self, other : GrammerRule) -> bool:
        return self.symbol == other.symbol and self.result == other.result