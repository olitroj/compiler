from enum import Enum

class NTermType(Enum):
    STATEMENT = None
    EXPRESSION = None

class NTerm:
    def __init__(self, type : NTermType, value = None) -> None:
        self.type = type
        self.value = value

    def __str__(self) -> str:
        return f"{self.type.name}({self.value})"
    
    def __eq__(self, other : NTerm) -> bool:
        return self.type == other.type and self.value == other.value