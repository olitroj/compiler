# AST -> What to expect
## Statements
Each statement starts with a STATEMENT node, and the child nodes are whatever the statement requires ex. VAR ID ASSIGN EXPRESSION
```
            STATMENT_LIST
            /           \
        STATEMENT      STATEMENT_LIST_NEXT
       /               /                \
    VAR...            ;             STATEMENT_LIST
                                          ...
```

## Expressions
Expressions are an AST. The operator is the root node, and the children are the operands. For unary operators, the operator is still the root, but the left child is None, and the right child is the operand. The lower the operator is on the tree, the higher the precedence.
```
                        +
                /               \
            +                       -
        /       \               /       \
    3           ||          None            5
            /       \
        x               y
```
This tree represents 3 + (x || y) + -5.

## How I would approach it
Write some assembly templetes for each type of statement, and for each type of operator. Traverse the tree, based on what you encounter generate the appropriate assembly based on the templetes.

For expressions, have a stack, and do post-order traversal (depth first). If you encounter a value, push to the stack. If you encounter an operator, pop the top values, do the operation on said values, and push the result. The AST is structured in a way such that if you do post-order traversal, the order of operations will be correct.