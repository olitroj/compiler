from syntax.grammer import N, grammer
from syntax.tree import Tree
from shared.tok import Token, TokenType as T
from shared.grammer import Symbol

'''
    Parsing function for analysing the syntactic structure of a sequence of tokens, based on the grammer.
    Creates a parse tree containing each rule used to derrive the given sequence of tokens.
    Removes redundant nodes ex. epsilon, non-terminal symbols with one child.

    Decides which rule fits by peeking two tokens (since the grammer is LL(2)).

    Returns a parse tree on success, or None if the sequence of tokens doesn't follow the grammer.
'''
def parse(tokens: list[Token]) -> Tree | None:
    tree = Tree(Symbol(N.STATEMENT_LIST))
    if _build_tree(tree, tokens, 0) == None:
        return None
    else:
        return tree

'''
    Recursive function for building a parse tree from a sequence of tokens.
    Returns None if not successful.
'''
def _build_tree(tree: Tree, tokens: list[Token], t_idx: int):
    # Go through all of the rules, check only the ones with a matching nterm
    # TODO : Go through the rules with terminal symbols first, then the ones with non-terminals
    for rule in grammer:
        if rule.nterm_type != tree.symbol.type:
            continue

        result = rule.result

        # If it reaches an epsilon rule, return t_idx without incrementing
        if result == None:
            return t_idx

        # Peek the next 2 symbols.
        # If there are no symbols left, or the symbol is terminal and doesn't match the rule, continue (try the next rule)
        if len(result) > 0:
            peek = _peek(tokens, t_idx, 0)
            if peek is None:
                continue
            elif result[0] in T and result[0] != peek.type:
                continue
        if len(result) > 1:
            peek = _peek(tokens, t_idx, 1)
            if peek is None:
                continue
            elif result[1] in T and result[1] != peek.type:
                continue

        # If the rule fits
        for rule_sym_type in result:
            peek = _peek(tokens, t_idx, 0)
            # Add terminal symbol to tree if it matches the rule, increment t_idx
            if rule_sym_type in T and peek is not None and rule_sym_type == peek.type:
                tree.nodes.append(Tree(tokens[t_idx]))
                t_idx += 1

            # Recursivly expand non-terminal symbols. Add the expanded node to the tree. Return None if expanding failed
            elif rule_sym_type in N:
                nterm_node = Tree(Symbol(rule_sym_type))
                t_idx = _build_tree(nterm_node, tokens, t_idx)
                if t_idx == None:
                    return None

                # These statements cut the tree if they are redundant
                # If non-terminal has only one child, replace it with the child (removes redendant non-terminal)
                if len(nterm_node.nodes) == 1 and nterm_node.symbol.type in N:
                    tree.nodes.append(nterm_node.nodes[0])
                # If node has no children (epsilon), remove it entirely (redundant)
                elif len(nterm_node.nodes) != 0:
                    tree.nodes.append(nterm_node)

            else:
                return None   
        return t_idx
    
def _peek(tokens: list[Token], t_idx: int, peek: int):
    if len(tokens) <= t_idx + peek:
        return None
    else:
        return tokens[t_idx + peek]