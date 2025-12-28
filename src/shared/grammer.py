from enum import Enum

'''
    Enum class that represents a symbol's type (terminal or non-terminal).
    Abstract classes, inherit to define symbols in a grammer.
'''
class SymbolType(Enum):
    pass
class TerminalType(SymbolType):
    pass
class NonTerminalType(SymbolType):
    pass

'''
    Classes that represent terminal or non-terminal symbols. Contain a [type], and an optional [value]
    Abstract class, inherit this class to define symbols in a grammer.
'''
class Symbol:
    def __init__(self, type : SymbolType, value = None) -> None:
        self.type = type
        self.value = value

    def __str__(self) -> str:
        return  f"{self.type.name}" if self.value == None else f"{self.type.name}({self.value})"
    
    def __eq__(self, other : Symbol) -> bool:
        return self.type == other.type and self.value == other.value
    
class Terminal(Symbol):
    pass
class NonTerminal(Symbol):
    pass

'''
    Class representing a production rule for a reguler or context-free grammer.
    A single non-terminal symbol [nterm] is transformed into a sequence of terminal/non-terminal symbols [result].
'''
class GrammerRule:
    def __init__(self, nterm : NonTerminalType, result : list[SymbolType] | None) -> None:
        self.nterm = nterm
        self.result = result

    def __str__(self) -> str:
        return f"{self.nterm.name} -> {' '.join(r.name for r in self.result)}"
    
    def __eq__(self, other : GrammerRule) -> bool:
        return self.nterm == other.nterm and self.result == other.result