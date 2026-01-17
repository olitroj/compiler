from shared.grammer import Symbol

'''
    Class representing an tree
    Each instance is a node, containing a [symbol], and optionally leaf [nodes].
    Leaf nodes are stored in a list, where the first node is the leftmost, and the last is the rightmost in the tree.
'''
class Tree:
    def __init__(self, symbol : Symbol, nodes : list[Tree] | None = None) -> None:
        self.symbol = symbol
        self.nodes = nodes if nodes is not None else []

    # def __eq__(self, other : Tree) -> bool:
    #     return self.symbol == other.symbol and self.nodes == other.nodes
    
    def __repr__(self) -> str:
        if not self.nodes:
            return repr(self.symbol)
        return f"({repr(self.symbol)} {' '.join(repr(n) for n in self.nodes)})"