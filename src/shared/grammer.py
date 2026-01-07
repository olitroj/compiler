from enum import Enum

'''
    Abstract enum class that represents a symbol type (terminal or non-terminal).
    Contains a [val], and a [is_terminal] flag.
    Inherit this class to create new symbol types.
'''
class SymbolType(Enum):
    def __init__(self, val, is_terminal: bool):
        self.val = val
        self.is_terminal = is_terminal

'''
    Abstract class that represents a terminal or non-terminal symbol.
    Contains a [type], and an optional [value]
    Tnherit this class to define new symbols in a grammer.
'''
class Symbol:
    def __init__(self, type: SymbolType, value = None) -> None:
        self.type = type
        self.value = value

    def __eq__(self, other: Symbol) -> bool:
        return self.type == other.type and self.value == other.value
    
    def __repr__(self) -> str:
        return self.type.name if self.value is None else f"{self.type.name}({repr(self.value)})"

'''
    Class representing a production rule for a reguler or context-free grammer.
    A single non-terminal symbol [nterm] transforms into a sequence of terminal and/or non-terminal symbols [result].
'''
class GrammerRule:
    def __init__(self, nterm_type: SymbolType, result: list[SymbolType] | None) -> None:
        if nterm_type.is_terminal:
            raise ValueError("nterm_type value of GrammerRule must be a non-terminal symbol type!")
        self.nterm_type = nterm_type
        self.result = result
        
    def __eq__(self, other: GrammerRule) -> bool:
        return self.nterm_type == other.nterm_type and self.result == other.result
    
    def __repr__(self) -> str:
        if self.result is None:
            return f"{self.nterm_type.name}->E"
        return f"{self.nterm_type}->" + " ".join(r.name for r in self.result)