from shared.tree import Tree
from shared.tok import Token, TokenType as T
from syntax.grammer_def import N

class CodeGenerator:
    """
    Generates 6502 assembly code (DASM syntax) from an AST.
    
    This is a single-pass, tree-walking code generator that directly translates
    AST nodes into 6502 assembly instructions. It uses a post-order traversal
    strategy for expressions to generate efficient stack-based evaluation code.
    
    Memory layout:
    - Zero page ($00-$0F): Reserved for system use
    - Zero page ($10-$FF): Variables allocated sequentially
    - $0200+: Expression evaluation stack
    - $0600+: Program code location
    
    Temporary zero-page locations used by generated code:
    - $FA: Input routine accumulator
    - $FB-$FD: Decimal output digit extraction
    - $FE: Binary operation right operand storage
    
    Target options:
    - 'generic': Default placeholder I/O addresses (template)
    - 'py65mon': py65mon emulator with console I/O (functional)
    
    Maximum variables: ~234 (theoretical limit 240, but upper zero-page reserved)
    """
    
    def __init__(self, target='generic'):
        """
        Initialize the code generator.
        
        Args:
            target: Target emulator ('generic' or 'py65mon')
        """
        self.variables = {}  # Maps variable name to zero-page address
        self.next_var_addr = 0x10  # Start variables at $10 (avoid system area $00-$0F)
        self.label_counter = 0  # Counter for generating unique labels
        self.stack_ptr = 0x0200  # Stack starts at $0200 (not actively used, for reference)
        self.output = []  # Accumulates lines of assembly code
        self.target = target  # Target emulator determines I/O implementation
        
    def generate(self, ast: Tree) -> str:
        """
        Generate complete assembly program from AST.
        
        This is the main entry point that orchestrates the entire code generation
        process. It produces a complete, executable 6502 assembly program.
        
        Structure of generated program:
        1. Header comments and assembler directives
        2. Stack pointer initialization
        3. Program body (statements from AST)
        4. Program termination (BRK instruction)
        5. I/O subroutines (input_routine, output_routine)
        
        Args:
            ast: The root of the abstract syntax tree (STATEMENT_LIST node)
            
        Returns:
            String containing complete DASM-format assembly code
        """
        self.output = []
        
        # ===== PROGRAM HEADER =====
        # Generate comments and DASM assembler directives
        self.emit("; Generated 6502 Assembly Code")
        self.emit("; Processor: 6502")
        self.emit("")
        
        self.emit("    processor 6502")
        self.emit("    org $0600    ; Start program at $0600")
        self.emit("")
        
        # ===== INITIALIZE HARDWARE STACK =====
        # The 6502 hardware stack lives at $0100-$01FF
        # We set stack pointer to $FF so stack grows down from $01FF
        self.emit("start:")
        self.emit("    LDX #$FF")
        self.emit("    TXS          ; Initialize stack pointer")
        self.emit("")
        
        # ===== PROGRAM BODY =====
        # Walk the AST and generate code for all statements
        self._gen_statement_list(ast)
        
        # ===== PROGRAM TERMINATION =====
        # BRK causes a software interrupt, stopping execution
        self.emit("")
        self.emit("    BRK          ; End program")
        self.emit("")
        
        # ===== I/O SUBROUTINES =====
        # Append target-specific input/output routines
        self._gen_io_routines()
        
        return "\n".join(self.output)
    
    def emit(self, code: str):
        """
        Add a line of assembly code to output buffer.
        
        All generated assembly instructions pass through this method,
        which accumulates them in the output list.
        
        Args:
            code: A single line of assembly code (with or without indentation)
        """
        self.output.append(code)
    
    def get_label(self, prefix: str = "L") -> str:
        """
        Generate a unique label for control flow.
        
        Labels are used for jumps and branches in if/else, loops, and
        complex expressions. Each call returns a new unique label.
        
        Args:
            prefix: Label prefix (e.g., "WHILE", "IF", "ELSE")
            
        Returns:
            Unique label string (e.g., "WHILE0", "WHILE1", "IF2")
        """
        label = f"{prefix}{self.label_counter}"
        self.label_counter += 1
        return label
    
    def allocate_variable(self, name: str) -> int:
        """
        Allocate a zero-page address for a variable.
        
        Variables are allocated sequentially starting at $10. Once a variable
        is allocated, its address remains fixed for the program's lifetime.
        
        Note: There's a practical limit of ~234 variables due to zero-page
        size (256 bytes) and reserved temporary locations ($FA-$FF).
        
        Args:
            name: Variable identifier
            
        Returns:
            Zero-page address (int) where variable is stored
            
        Raises:
            RuntimeError: If zero-page memory is exhausted (>255 variables)
        """
        if name not in self.variables:
            if self.next_var_addr > 0xFF:
                raise RuntimeError("Out of zero-page memory for variables!")
            self.variables[name] = self.next_var_addr
            self.next_var_addr += 1
        return self.variables[name]
    
    def get_variable_addr(self, name: str) -> int:
        """
        Get the zero-page address of a previously allocated variable.
        
        Args:
            name: Variable identifier
            
        Returns:
            Zero-page address where variable is stored
            
        Raises:
            RuntimeError: If variable was never allocated (semantic error)
        """
        if name not in self.variables:
            raise RuntimeError(f"Variable '{name}' not allocated!")
        return self.variables[name]
    
    # ==================== Statement Generation ====================
    # These methods walk the AST and generate code for different statement types.
    # They follow the grammar structure, matching AST node patterns and dispatching
    # to appropriate handlers.
    
    def _gen_statement_list(self, node: Tree):
        """
        Generate code for a list of statements (the program body).
        
        Grammar: STATEMENT_LIST -> STATEMENT STATEMENT_LIST_NEXT
        
        This recursively processes all statements in the program, generating
        assembly code for each one in sequence.
        
        Args:
            node: STATEMENT_LIST AST node
        """
        if node is None:
            return
        if node.symbol.type == N.STATEMENT_LIST:
            # Generate code for first statement
            self._gen_statement(node.nodes[0])
            # Process remaining statements (if any)
            if len(node.nodes) > 1:
                self._gen_statement_list_next(node.nodes[1])
    
    def _gen_statement_list_next(self, node: Tree):
        """
        Generate code for the continuation of a statement list.
        
        Grammar: STATEMENT_LIST_NEXT -> SEMICOLON STATEMENT_LIST | epsilon
        
        Handles the recursive part of statement lists. If more statements exist,
        it recursively calls back to _gen_statement_list.
        
        Args:
            node: STATEMENT_LIST_NEXT AST node
        """
        if node is None:
            return
        if node.symbol.type == N.STATEMENT_LIST_NEXT:
            if len(node.nodes) > 1:  # Has more statements
                self._gen_statement_list(node.nodes[1])
    
    def _gen_statement(self, node: Tree):
        """
        Generate code for a single statement (dispatcher).
        
        This is the main statement dispatcher that examines the first token
        of a statement and routes to the appropriate handler. It implements
        pattern matching on AST structure to identify statement types.
        
        Supported statement types:
        - Variable declarations: var x = <expr>
        - Assignments: x = <expr>
        - Increment/decrement: x++, x--
        - If/else statements
        - While loops
        - Do-while loops
        - Function calls: input(), output()
        - Statement blocks: { ... }
        
        Args:
            node: STATEMENT AST node
        """
        if node is None:
            return
        
        children = node.nodes
        
        if not children:
            return
        
        first_token = children[0].symbol
        
        # ===== VARIABLE DECLARATION =====
        # Pattern: VAR ID ASSIGN EXPRESSION
        # Example: var x = 5
        if first_token.type == T.VAR:
            # Allocate zero-page memory for new variable
            var_name = children[1].symbol.value
            addr = self.allocate_variable(var_name)
            self.emit(f"    ; var {var_name} = <expression>")
            # Evaluate expression, result left in accumulator A
            self._gen_expression(children[3])
            # Store accumulator to variable's zero-page address
            self.emit(f"    STA ${addr:02X}        ; Store to {var_name}")
            self.emit("")
        
        # ===== ASSIGNMENT =====
        # Pattern: ID ASSIGN EXPRESSION
        # Example: x = y + 3
        elif first_token.type == T.ID and len(children) > 1 and children[1].symbol.type == T.ASSIGN:
            var_name = children[0].symbol.value
            addr = self.get_variable_addr(var_name)
            self.emit(f"    ; {var_name} = <expression>")
            # Evaluate expression, result in A
            self._gen_expression(children[2])
            # Store to existing variable
            self.emit(f"    STA ${addr:02X}        ; Store to {var_name}")
            self.emit("")
        
        # ===== INCREMENT =====
        # Pattern: ID INCREMENT
        # Example: x++
        # Uses efficient 6502 INC instruction (single cycle)
        elif first_token.type == T.ID and len(children) > 1 and children[1].symbol.type == T.INCREMENT:
            var_name = children[0].symbol.value
            addr = self.get_variable_addr(var_name)
            self.emit(f"    ; {var_name}++")
            self.emit(f"    INC ${addr:02X}")
            self.emit("")
        
        # ===== DECREMENT =====
        # Pattern: ID DECREMENT
        # Example: x--
        # Uses efficient 6502 DEC instruction (single cycle)
        elif first_token.type == T.ID and len(children) > 1 and children[1].symbol.type == T.DECREMENT:
            var_name = children[0].symbol.value
            addr = self.get_variable_addr(var_name)
            self.emit(f"    ; {var_name}--")
            self.emit(f"    DEC ${addr:02X}")
            self.emit("")
        
        # ===== IF STATEMENT =====
        # Delegate to specialized handler for if/else logic
        elif first_token.type == T.IF:
            self._gen_if_statement(children)
        
        # ===== WHILE LOOP =====
        # Delegate to specialized handler for while loops
        elif first_token.type == T.WHILE:
            self._gen_while_statement(children)
        
        # ===== DO-WHILE LOOP =====
        # Delegate to specialized handler for do-while loops
        elif first_token.type == T.DO:
            self._gen_do_while_statement(children)
        
        # ===== FUNCTION CALL =====
        # Pattern: ID OPEN_BRACE EXPRESSION_LIST
        # Currently supports: input(), output(value)
        elif first_token.type == T.ID and len(children) > 1 and children[1].symbol.type == T.OPEN_BRACE:
            self._gen_function_call(children)
        
        # ===== STATEMENT BLOCK =====
        # Pattern: OPEN_CURLY GROUP_LIST CLOSE_CURLY
        # Example: { statement1; statement2; }
        elif first_token.type == T.OPEN_CURLY:
            self._gen_group_list(children[1])
    
    def _gen_if_statement(self, children):
        """
        Generate if/else statement with conditional branching.
        
        Pattern: IF EXPRESSION STATEMENT ELSE_CLAUSE
        
        Generated code structure:
            ; Evaluate condition
            CMP #0
            BEQ ELSE0        ; Jump if false (condition == 0)
            ; Then branch code
            JMP ENDIF0       ; Skip else
        ELSE0:
            ; Else branch code (if present)
        ENDIF0:
        
        Uses C convention: 0 = false, non-zero = true
        
        Args:
            children: Child nodes of the if statement [IF, EXPRESSION, STATEMENT, ELSE_CLAUSE]
        """
        self.emit("    ; if statement")
        
        # Evaluate condition expression, result in accumulator A
        # 0 = false, any non-zero value = true
        self._gen_expression(children[1])
        
        # Generate unique labels for control flow
        else_label = self.get_label("ELSE")
        end_label = self.get_label("ENDIF")
        
        # Test condition: compare accumulator to zero
        self.emit("    CMP #0")
        self.emit(f"    BEQ {else_label}    ; Jump to else if false")
        self.emit("")
        
        # ===== THEN BRANCH =====
        self._gen_statement(children[2])
        self.emit(f"    JMP {end_label}     ; Skip else branch")
        self.emit("")
        
        # ===== ELSE BRANCH =====
        self.emit(f"{else_label}:")
        if len(children) > 3:
            else_clause = children[3]
            if else_clause.nodes:  # Has else statement
                self._gen_statement(else_clause.nodes[1])
        
        self.emit(f"{end_label}:")
        self.emit("")
    
    def _gen_while_statement(self, children):
        """
        Generate while loop (condition tested before body).
        
        Pattern: WHILE EXPRESSION STATEMENT
        
        Generated code structure:
        WHILE0:
            ; Evaluate condition
            CMP #0
            BEQ ENDWHILE0    ; Exit if false
            ; Loop body
            JMP WHILE0       ; Repeat
        ENDWHILE0:
        
        The condition is checked before each iteration, so the body
        may never execute if the condition is initially false.
        
        Args:
            children: Child nodes [WHILE, EXPRESSION, STATEMENT]
        """
        loop_start = self.get_label("WHILE")
        loop_end = self.get_label("ENDWHILE")
        
        # Loop entry point - condition is tested here
        self.emit(f"{loop_start}:")
        self.emit("    ; while condition")
        
        # Evaluate loop condition
        self._gen_expression(children[1])
        
        # Exit loop if condition is false (A == 0)
        self.emit("    CMP #0")
        self.emit(f"    BEQ {loop_end}      ; Exit loop if false")
        self.emit("")
        
        # ===== LOOP BODY =====
        self._gen_statement(children[2])
        
        # Jump back to condition check
        self.emit(f"    JMP {loop_start}    ; Loop back")
        self.emit(f"{loop_end}:")
        self.emit("")
    
    def _gen_do_while_statement(self, children):
        """
        Generate do-while loop (condition tested after body).
        
        Pattern: DO STATEMENT WHILE EXPRESSION
        
        Generated code structure:
        DO0:
            ; Loop body
            ; Evaluate condition
            CMP #0
            BNE DO0          ; Continue if true
        
        The body always executes at least once, since the condition
        is checked after the first iteration.
        
        Args:
            children: Child nodes [DO, STATEMENT, WHILE, EXPRESSION]
        """
        loop_start = self.get_label("DO")
        
        # Loop entry point
        self.emit(f"{loop_start}:")
        self.emit("    ; do-while body")
        
        # ===== LOOP BODY =====
        # Body executes before condition check
        self._gen_statement(children[1])
        
        # Evaluate condition after body
        self.emit("    ; while condition")
        self._gen_expression(children[3])
        
        # Continue loop if condition is true (A != 0)
        self.emit("    CMP #0")
        self.emit(f"    BNE {loop_start}    ; Loop if true")
        self.emit("")
    
    def _gen_function_call(self, children):
        """
        Generate function call statement.
        
        Pattern: ID OPEN_BRACE EXPRESSION_LIST CLOSE_BRACE
        
        Currently supports two built-in functions:
        - output(value): Outputs a value (result in A before JSR)
        - input(): Reads input (result returned in A after JSR)
        
        Uses JSR (Jump to SubRoutine) instruction to call I/O routines
        that are appended at the end of the generated program.
        
        Args:
            children: Child nodes [ID, OPEN_BRACE, EXPRESSION_LIST, CLOSE_BRACE]
        """
        func_name = children[0].symbol.value
        
        if func_name == "output":
            # Extract argument from expression list
            expr_list = children[2]
            if expr_list.nodes and expr_list.nodes[0].symbol.type == N.EXPRESSION:
                self.emit("    ; output(<value>)")
                # Evaluate argument, result in A
                self._gen_expression(expr_list.nodes[0])
                # Call output routine (expects value in A)
                self.emit("    JSR output_routine")
                self.emit("")
        
        elif func_name == "input":
            self.emit("    ; input()")
            # Call input routine (returns value in A)
            self.emit("    JSR input_routine")
            self.emit("")
    
    def _gen_group_list(self, node: Tree):
        """
        Generate code for a statement block/group.
        
        Grammar: GROUP_LIST -> STATEMENT GROUP_LIST_NEXT
        
        Handles blocks like: { statement1; statement2; statement3; }
        Statements are executed sequentially.
        
        Args:
            node: GROUP_LIST AST node
        """
        if node is None:
            return
        if node.symbol.type == N.GROUP_LIST:
            # Generate first statement in block
            self._gen_statement(node.nodes[0])
            # Process remaining statements
            if len(node.nodes) > 1:
                self._gen_group_list_next(node.nodes[1])
    
    def _gen_group_list_next(self, node: Tree):
        """
        Generate code for continuation of statement block.
        
        Grammar: GROUP_LIST_NEXT -> SEMICOLON GROUP_LIST | epsilon
        
        Recursively processes remaining statements in a block.
        
        Args:
            node: GROUP_LIST_NEXT AST node
        """
        if node is None:
            return
        if node.symbol.type == N.GROUP_LIST_NEXT and len(node.nodes) > 1:
            self._gen_group_list(node.nodes[1])
    
    # ==================== Expression Generation ====================
    # Expression generation uses POST-ORDER TRAVERSAL to evaluate expression trees.
    # This naturally implements stack-based evaluation:
    #   1. Evaluate left subtree (result in A, save to stack)
    #   2. Evaluate right subtree (result in A)
    #   3. Apply operator (pop left from stack, operate with A)
    #
    # Result is always left in the accumulator register (A).
    
    def _gen_expr_tree(self, node: Tree):
        """
        Generate code for expression tree node using post-order traversal.
        
        This is the core expression evaluator. It recursively walks the expression
        tree in post-order (left-right-root), generating assembly code that
        evaluates the expression and leaves the result in accumulator A.
        
        Expression tree structure (created by semantic analyzer):
        - Leaf nodes: LITERAL (constants) or ID (variables)
        - Binary operators: (OPERATOR left_subtree right_subtree)
        - Unary operators: (OPERATOR None operand_subtree)
        - Function calls: VALUE nodes with special structure
        
        Evaluation strategy:
        For binary ops (e.g., a + b):
          1. Generate code for left operand → result in A
          2. Push A to hardware stack (PHA)
          3. Generate code for right operand → result in A
          4. Pop left operand from stack (PLA)
          5. Apply operation, result in A
        
        For unary ops (e.g., -x):
          1. Generate code for operand → result in A
          2. Apply operation in-place, result in A
        
        Args:
            node: Expression tree node (operator or operand)
        """
        if node is None:
            return
        
        sym = node.symbol
        sym_type = sym.type
        
        # ===== UNWRAP NESTED EXPRESSION NODES =====
        # Sometimes the grammar nesting creates EXPRESSION nodes within expression trees
        # (particularly with comparison operators). We unwrap these to get to the actual operator.
        if sym_type == N.EXPRESSION:
            if node.nodes:
                self._gen_expr_tree(node.nodes[0])
            return
        
        # ===== HANDLE FUNCTION CALLS IN EXPRESSIONS =====
        # Function calls like input() can appear as values in expressions
        # Example: var x = input() + 5
        # Pattern: VALUE -> ID OPEN_BRACE EXPRESSION_LIST NEXT_P5
        if sym_type == N.VALUE and len(node.nodes) >= 3:
            if (node.nodes[0].symbol.type == T.ID and 
                node.nodes[1].symbol.type == T.OPEN_BRACE):
                # This is a function call within an expression
                func_name = node.nodes[0].symbol.value
                expr_list = node.nodes[2]  # EXPRESSION_LIST
                
                if func_name == "input":
                    # input() returns value in A
                    self.emit("    ; input() function call")
                    self.emit("    JSR input_routine")
                elif func_name == "output":
                    # output() with argument (side effect, also returns value in A)
                    if expr_list.nodes and expr_list.nodes[0].symbol.type == N.EXPRESSION:
                        self.emit("    ; output(<value>) function call")
                        self._gen_expression(expr_list.nodes[0])
                        self.emit("    JSR output_routine")
                # Continue with NEXT_P5 if present (for chained operations)
                if len(node.nodes) > 3:
                    self._gen_expr_tree(node.nodes[3])
                return
        
        # ===== BASE CASE: LITERAL =====
        # Load immediate value into accumulator
        # Example: 5 → LDA #$05
        if sym_type == T.LITERAL:
            self.emit(f"    LDA #${sym.value:02X}      ; Load literal {sym.value}")
            return
        
        # ===== BASE CASE: VARIABLE =====
        # Load variable from its zero-page address
        # Example: x → LDA $10 (if x is at $10)
        if sym_type == T.ID:
            addr = self.get_variable_addr(sym.value)
            self.emit(f"    LDA ${addr:02X}        ; Load {sym.value}")
            return
        
        # ===== UNARY OPERATORS =====
        # Pattern: (OPERATOR None operand)
        # Left child is None to distinguish from binary operators
        if len(node.nodes) >= 2 and node.nodes[0] is None:
            # Generate code for operand first
            self._gen_expr_tree(node.nodes[1])  # Result in A
            
            # ----- UNARY MINUS -----
            # Negation using two's complement: invert all bits, then add 1
            # Example: -(5) → EOR #$FF, ADC #1 → -5
            if sym_type == T.MINUS:
                self.emit("    EOR #$FF        ; One's complement")
                self.emit("    CLC")
                self.emit("    ADC #1          ; Two's complement (negate)")
            
            # ----- BITWISE NOT -----
            # Invert all bits: ~x
            # Example: ~5 (00000101) → 250 (11111010)
            elif sym_type == T.BIT_NOT:
                self.emit("    EOR #$FF        ; Bitwise NOT")
            
            # ----- LOGICAL NOT -----
            # Boolean NOT: !x returns 1 if x==0, else 0
            # Implements: result = (operand == 0) ? 1 : 0
            elif sym_type == T.LOGIC_NOT:
                label_false = self.get_label("LNOT_F")
                label_end = self.get_label("LNOT_E")
                self.emit("    CMP #0")
                self.emit(f"    BNE {label_false}")
                self.emit("    LDA #1          ; Was zero, return 1")
                self.emit(f"    JMP {label_end}")
                self.emit(f"{label_false}:")
                self.emit("    LDA #0          ; Was non-zero, return 0")
                self.emit(f"{label_end}:")
            return
        
        # ===== BINARY OPERATORS =====
        # Pattern: (OPERATOR left right)
        # Standard post-order evaluation with stack for left operand
        if len(node.nodes) >= 2:
            left = node.nodes[0]
            right = node.nodes[1]
            
            # Step 1: Evaluate left subtree (result in A)
            self._gen_expr_tree(left)
            
            # Step 2: Save left operand to hardware stack
            self.emit("    PHA             ; Save left operand")
            
            # Step 3: Evaluate right subtree (result in A)
            # This may overwrite A, but left operand is safely on stack
            self._gen_expr_tree(right)
            
            # Step 4: Apply the operator
            # Right operand is in A, left operand is on stack
            # Most operations: pop left, store right in $FE, operate, result in A
            
            # ----- ADDITION -----
            # left + right
            if sym_type == T.PLUS:
                self.emit("    STA $FE         ; Save right operand")
                self.emit("    PLA             ; Restore left operand")
                self.emit("    CLC")
                self.emit("    ADC $FE         ; Add")
            
            # ----- SUBTRACTION -----
            # left - right
            # Uses SEC (set carry) for borrow
            elif sym_type == T.MINUS:
                self.emit("    STA $FE         ; Save right operand")
                self.emit("    PLA             ; Restore left operand")
                self.emit("    SEC")
                self.emit("    SBC $FE         ; Subtract")
            
            # ----- BITWISE AND -----
            # left & right (bit-by-bit AND)
            elif sym_type == T.BIT_AND:
                self.emit("    STA $FE         ; Save right operand")
                self.emit("    PLA             ; Restore left operand")
                self.emit("    AND $FE         ; Bitwise AND")
            
            # ----- BITWISE OR -----
            # left | right (bit-by-bit OR)
            elif sym_type == T.BIT_OR:
                self.emit("    STA $FE         ; Save right operand")
                self.emit("    PLA             ; Restore left operand")
                self.emit("    ORA $FE         ; Bitwise OR")
            
            # ----- BITWISE XOR -----
            # left ^ right (bit-by-bit exclusive OR)
            elif sym_type == T.BIT_XOR:
                self.emit("    STA $FE         ; Save right operand")
                self.emit("    PLA             ; Restore left operand")
                self.emit("    EOR $FE         ; Bitwise XOR")
            
            # ----- SHIFT LEFT -----
            # left << right (multiply by 2^right)

            elif sym_type == T.SHIFT_LEFT:
                self._gen_shift_left()
            
            # ----- SHIFT RIGHT -----
            # left >> right (divide by 2^right)

            elif sym_type == T.SHIFT_RIGHT:
                self._gen_shift_right()
            
            # ----- LOGICAL AND -----
            # left && right (returns 1 if both non-zero, else 0)

            elif sym_type == T.LOGIC_AND:
                self._gen_logical_and()
            
            # ----- LOGICAL OR -----
            # left || right (returns 1 if either non-zero, else 0)

            elif sym_type == T.LOGIC_OR:
                self._gen_logical_or()
            
            # ----- LOGICAL XOR -----
            # left ^^ right (returns 1 if exactly one is non-zero, else 0)

            elif sym_type == T.LOGIC_XOR:
                self._gen_logical_xor()
            
            # ----- EQUALITY -----
            # left == right (returns 1 if equal, else 0)
            elif sym_type == T.EQUAL:
                self._gen_equal()
            
            # ----- INEQUALITY -----
            # left != right (returns 1 if not equal, else 0)
            elif sym_type == T.NOT_EQUAL:
                self._gen_not_equal()
            
            # ----- LESS THAN -----
            # left < right (returns 1 if true, else 0)
            elif sym_type == T.LESS_THAN:
                self._gen_less_than()
            
            # ----- LESS THAN OR EQUAL -----
            # left <= right (returns 1 if true, else 0)
            elif sym_type == T.LESS_THAN_EQUALS:
                self._gen_less_than_equals()
            
            # ----- GREATER THAN -----
            # left > right (returns 1 if true, else 0)
            elif sym_type == T.GREATER_THAN:
                self._gen_greater_than()
            
            # ----- GREATER THAN OR EQUAL -----
            # left >= right (returns 1 if true, else 0)
            elif sym_type == T.GREATER_THAN_EQUALS:
                self._gen_greater_than_equals()
            
            return
    
    def _gen_expression(self, node: Tree):
        """
        Generate code for expression (entry point).
        
        This is the public entry point for expression code generation.
        It expects an EXPRESSION node from the AST and delegates to
        _gen_expr_tree for the actual code generation.
        
        The semantic analyzer restructures the parse tree into an expression
        tree where:
        - EXPRESSION node contains a single child (the root of the tree)
        - Operators are internal nodes with operands as children
        - Literals and variables are leaf nodes
        
        Result is always left in accumulator A.
        
        Args:
            node: EXPRESSION AST node from semantic analyzer
        """
        if node is None:
            return
        if node.symbol.type != N.EXPRESSION:
            return
        
        # Expression always has one child: the root of the expression tree
        if not node.nodes:
            return
        
        # Delegate to recursive tree walker
        self._gen_expr_tree(node.nodes[0])
    
    # ==================== Binary Operator Helpers ====================
    # These methods generate code for complex operations that require
    # loops or multiple branches. They are called with:
    #   - Right operand in accumulator A
    #   - Left operand on hardware stack
    # They must leave the result in accumulator A.
    
    def _gen_shift_left(self):
        """
        Generate left shift: left << right.
        
        Multiplies left by 2^right using repeated ASL (arithmetic shift left).
        Since the 6502 doesn't have a shift-by-count instruction, we use a loop.
        
        Entry: A = shift count (right operand), stack = value (left operand)
        Exit: A = shifted result
        
        Example: 3 << 2 = 12 (shift 3 left by 2 positions)
        """
        self.emit("    TAX             ; Shift count in X")
        self.emit("    PLA             ; Get value")
        loop_label = self.get_label("SHL")
        end_label = self.get_label("SHL_E")
        self.emit(f"{loop_label}:")
        self.emit("    CPX #0")
        self.emit(f"    BEQ {end_label}")
        self.emit("    ASL             ; Shift left accumulator")
        self.emit("    DEX")
        self.emit(f"    JMP {loop_label}")
        self.emit(f"{end_label}:")
    
    def _gen_shift_right(self):
        """
        Generate right shift: left >> right.
        
        Divides left by 2^right using repeated LSR (logical shift right).
        Uses a loop since 6502 lacks variable-count shift instructions.
        
        Entry: A = shift count (right operand), stack = value (left operand)
        Exit: A = shifted result
        
        Example: 12 >> 2 = 3 (shift 12 right by 2 positions)
        """
        self.emit("    TAX             ; Shift count in X")
        self.emit("    PLA             ; Get value")
        loop_label = self.get_label("SHR")
        end_label = self.get_label("SHR_E")
        self.emit(f"{loop_label}:")
        self.emit("    CPX #0")
        self.emit(f"    BEQ {end_label}")
        self.emit("    LSR             ; Shift right accumulator")
        self.emit("    DEX")
        self.emit(f"    JMP {loop_label}")
        self.emit(f"{end_label}:")
    
    def _gen_logical_and(self):
        """
        Generate logical AND: left && right.
        
        Boolean AND operation: returns 1 if both operands are non-zero, else 0.
        Treats any non-zero value as true, zero as false.
        
        Entry: A = right operand, stack = left operand
        Exit: A = 1 (both true) or 0 (at least one false)
        
        Truth table:
        - left=0, right=0 → 0
        - left=0, right≠0 → 0
        - left≠0, right=0 → 0
        - left≠0, right≠0 → 1
        """
        self.emit("    TAY             ; Save right in Y")
        self.emit("    PLA             ; Get left")
        label_false = self.get_label("AND_F")
        label_end = self.get_label("AND_E")
        self.emit("    CMP #0")
        self.emit(f"    BEQ {label_false}   ; Left is false")
        self.emit("    TYA             ; Check right")
        self.emit("    CMP #0")
        self.emit(f"    BEQ {label_false}   ; Right is false")
        self.emit("    LDA #1          ; Both true")
        self.emit(f"    JMP {label_end}")
        self.emit(f"{label_false}:")
        self.emit("    LDA #0          ; At least one false")
        self.emit(f"{label_end}:")
    
    def _gen_logical_or(self):
        """
        Generate logical OR: left || right.
        
        Boolean OR operation: returns 1 if either operand is non-zero, else 0.
        Treats any non-zero value as true, zero as false.
        
        Entry: A = right operand, stack = left operand
        Exit: A = 1 (at least one true) or 0 (both false)
        
        Truth table:
        - left=0, right=0 → 0
        - left=0, right≠0 → 1
        - left≠0, right=0 → 1
        - left≠0, right≠0 → 1
        """
        self.emit("    TAY             ; Save right in Y")
        self.emit("    PLA             ; Get left")
        label_true = self.get_label("OR_T")
        label_false = self.get_label("OR_F")
        label_end = self.get_label("OR_E")
        self.emit("    CMP #0")
        self.emit(f"    BNE {label_true}    ; Left is true")
        self.emit("    TYA             ; Check right")
        self.emit("    CMP #0")
        self.emit(f"    BNE {label_true}    ; Right is true")
        self.emit(f"    JMP {label_false}")
        self.emit(f"{label_true}:")
        self.emit("    LDA #1          ; At least one true")
        self.emit(f"    JMP {label_end}")
        self.emit(f"{label_false}:")
        self.emit("    LDA #0          ; Both false")
        self.emit(f"{label_end}:")
    
    def _gen_logical_xor(self):
        """
        Generate logical XOR: left ^^ right.
        
        Boolean XOR operation: returns 1 if exactly one operand is non-zero, else 0.
        Treats any non-zero value as true, zero as false.
        
        Entry: A = right operand, stack = left operand
        Exit: A = 1 (exactly one true) or 0 (both true or both false)
        
        Truth table:
        - left=0, right=0 → 0
        - left=0, right≠0 → 1
        - left≠0, right=0 → 1
        - left≠0, right≠0 → 0
        """
        self.emit("    TAY             ; Save right in Y")
        self.emit("    PLA             ; Get left")
        label_l_true = self.get_label("XOR_LT")
        label_l_false = self.get_label("XOR_LF")
        label_result_true = self.get_label("XOR_RT")
        label_result_false = self.get_label("XOR_RF")
        label_end = self.get_label("XOR_E")
        self.emit("    CMP #0")
        self.emit(f"    BNE {label_l_true}")
        self.emit(f"{label_l_false}:")
        self.emit("    TYA")
        self.emit("    CMP #0")
        self.emit(f"    BEQ {label_result_false}  ; L=F, R=F -> F")
        self.emit(f"    JMP {label_result_true}   ; L=F, R=T -> T")
        self.emit(f"{label_l_true}:")
        self.emit("    TYA")
        self.emit("    CMP #0")
        self.emit(f"    BEQ {label_result_true}   ; L=T, R=F -> T")
        self.emit(f"    JMP {label_result_false}  ; L=T, R=T -> F")
        self.emit(f"{label_result_true}:")
        self.emit("    LDA #1")
        self.emit(f"    JMP {label_end}")
        self.emit(f"{label_result_false}:")
        self.emit("    LDA #0")
        self.emit(f"{label_end}:")
    
    def _gen_equal(self):
        """
        Generate equality comparison: left == right.
        
        Returns 1 if operands are equal, 0 otherwise.
        Uses CMP instruction which sets flags based on subtraction.
        
        Entry: A = right operand, stack = left operand
        Exit: A = 1 (equal) or 0 (not equal)
        """
        self.emit("    STA $FE         ; Save right operand")
        self.emit("    PLA             ; Restore left operand")
        label_true = self.get_label("EQ_T")
        label_end = self.get_label("EQ_E")
        self.emit("    CMP $FE")
        self.emit(f"    BEQ {label_true}")
        self.emit("    LDA #0          ; Not equal")
        self.emit(f"    JMP {label_end}")
        self.emit(f"{label_true}:")
        self.emit("    LDA #1          ; Equal")
        self.emit(f"{label_end}:")
    
    def _gen_not_equal(self):
        """
        Generate inequality comparison: left != right.
        
        Returns 1 if operands are not equal, 0 if equal.
        Uses CMP instruction which sets flags based on subtraction.
        
        Entry: A = right operand, stack = left operand
        Exit: A = 1 (not equal) or 0 (equal)
        """
        self.emit("    STA $FE         ; Save right operand")
        self.emit("    PLA             ; Restore left operand")
        label_true = self.get_label("NE_T")
        label_end = self.get_label("NE_E")
        self.emit("    CMP $FE")
        self.emit(f"    BNE {label_true}")
        self.emit("    LDA #0          ; Equal")
        self.emit(f"    JMP {label_end}")
        self.emit(f"{label_true}:")
        self.emit("    LDA #1          ; Not equal")
        self.emit(f"{label_end}:")
    
    # ==================== Comparison Helpers ====================
    # These generate relational comparison operations (<, >, <=, >=).
    # Entry: A = right operand, stack = left operand
    # Exit: A = 1 (condition true) or 0 (condition false)
    #
    # Uses CMP instruction which performs: left - right
    # and sets processor flags based on result:
    #   - Carry flag clear (BCC) means left < right
    #   - Zero flag set (BEQ) means left == right
    
    def _gen_less_than(self):
        """
        Generate less than comparison: left < right.
        
        Uses BCC (Branch if Carry Clear) after CMP.
        CMP performs left - right and clears carry if result is negative (left < right).
        
        Returns 1 if left < right, else 0.
        """
        self.emit("    STA $FE         ; Save right operand")
        self.emit("    PLA             ; Restore left operand")
        label_true = self.get_label("LT_T")
        label_end = self.get_label("LT_E")
        self.emit("    CMP $FE         ; Compare left with right")
        self.emit(f"    BCC {label_true}    ; Branch if left < right")
        self.emit("    LDA #0          ; False")
        self.emit(f"    JMP {label_end}")
        self.emit(f"{label_true}:")
        self.emit("    LDA #1          ; True")
        self.emit(f"{label_end}:")
    
    def _gen_less_than_equals(self):
        """
        Generate less than or equal: left <= right.
        
        Combines BCC (less than) and BEQ (equal) checks.
        Returns 1 if left <= right, else 0.
        """
        self.emit("    STA $FE         ; Save right operand")
        self.emit("    PLA             ; Restore left operand")
        label_true = self.get_label("LE_T")
        label_end = self.get_label("LE_E")
        self.emit("    CMP $FE         ; Compare left with right")
        self.emit(f"    BCC {label_true}    ; Branch if left < right")
        self.emit(f"    BEQ {label_true}    ; Branch if left == right")
        self.emit("    LDA #0          ; False")
        self.emit(f"    JMP {label_end}")
        self.emit(f"{label_true}:")
        self.emit("    LDA #1          ; True")
        self.emit(f"{label_end}:")
    
    def _gen_greater_than(self):
        """
        Generate greater than comparison: left > right.
        
        Returns false if equal or less than (using BEQ and BCC).
        Otherwise returns true.
        Returns 1 if left > right, else 0.
        """
        self.emit("    STA $FE         ; Save right operand")
        self.emit("    PLA             ; Restore left operand")
        label_false = self.get_label("GT_F")
        label_end = self.get_label("GT_E")
        self.emit("    CMP $FE         ; Compare left with right")
        self.emit(f"    BEQ {label_false}     ; Equal, return 0")
        self.emit(f"    BCC {label_false}     ; left < right, return 0")
        self.emit("    LDA #1          ; left > right")
        self.emit(f"    JMP {label_end}")
        self.emit(f"{label_false}:")
        self.emit("    LDA #0          ; Not greater")
        self.emit(f"{label_end}:")
    
    def _gen_greater_than_equals(self):
        """
        Generate greater than or equal: left >= right.
        
        Uses BCC to check for less than. If not less than, then >= is true.
        Returns 1 if left >= right, else 0.
        """
        self.emit("    STA $FE         ; Save right operand")
        self.emit("    PLA             ; Restore left operand")
        label_false = self.get_label("GE_F")
        label_end = self.get_label("GE_E")
        self.emit("    CMP $FE         ; Compare left with right")
        self.emit(f"    BCC {label_false}     ; left < right, return 0")
        self.emit("    LDA #1          ; left >= right")
        self.emit(f"    JMP {label_end}")
        self.emit(f"{label_false}:")
        self.emit("    LDA #0          ; Less than")
        self.emit(f"{label_end}:")
    
    # ==================== I/O Routines ====================
    # These methods generate input/output subroutines appended to the program.
    # Different implementations are provided for different target emulators
    # since I/O is not standardized in the 6502 architecture.
    
    def _gen_io_routines(self):
        """
        Generate I/O subroutines based on target emulator.
        
        Appends input_routine and output_routine subroutines to the program.
        The implementation varies based on the target emulator's I/O mechanism.
        
        Targets:
        - 'py65mon': Uses memory-mapped console I/O at $F001/$F004
        - 'generic': Placeholder using example memory-mapped addresses
        """
        self.emit("; ==================== I/O Routines ====================")
        self.emit("")
        
        if self.target == 'py65mon':
            self._gen_py65mon_io()
        else:
            self._gen_generic_io()
    
    def _gen_generic_io(self):
        """
        Generate generic placeholder I/O routines.
        
        These are template routines using hypothetical memory-mapped I/O addresses.
        They won't actually work on any real hardware or emulator, but serve as
        a starting point for porting to new platforms.
        
        To port to a new platform, replace $D010/$D012 with actual I/O addresses.
        """
        self.emit("output_routine:")
        self.emit("    ; Output value in A to screen/console")
        self.emit("    ; For 6502, this is system-dependent")
        self.emit("    ; Here we write to memory-mapped I/O at $D012 (example)")
        self.emit("    STA $D012       ; Write to output port")
        self.emit("    RTS")
        self.emit("")
        self.emit("input_routine:")
        self.emit("    ; Read input value into A")
        self.emit("    ; For 6502, this is system-dependent")
        self.emit("    ; Here we read from memory-mapped I/O at $D010 (example)")
        self.emit("    LDA $D010       ; Read from input port")
        self.emit("    RTS")
        self.emit("")
    
    def _gen_py65mon_io(self):
        """
        Generate I/O routines for py65mon emulator.
        
        py65mon provides memory-mapped console I/O:
        - $F001: Write ASCII character to output (console)
        - $F005: Blocking input (0 if no key pressed)
        
        The output routine converts binary (0-255) to decimal ASCII for readability.
        The input routine reads multi-digit decimal numbers until Enter is pressed.
        
        Uses zero-page temporaries:
        - $FA: Input accumulator
        - $FB: Number being processed for output
        - $FC: (unused)
        - $FD: Leading zero suppression flag
        - $FE: Temporary digit storage
        """
        self.emit("; Target: py65mon emulator")
        self.emit("; Console output at $F001, blocking input at $F005")
        self.emit("")
        self.emit("output_routine:")
        self.emit("    ; Output value in A as decimal number (0-255)")
        self.emit("    ; Uses zero-page $FB-$FD for temporary storage")
        self.emit("    ; Algorithm: Repeatedly divide by 100, 10 to extract digits")
        self.emit("    ; Suppresses leading zeros (e.g., 5 prints as '5' not '005')")
        self.emit("    STA $FB          ; Store number to output")
        self.emit("    LDA #1")
        self.emit("    STA $FD          ; Start suppressing leading zeros")
        self.emit("")
        self.emit("    ; ===== Output hundreds digit =====")
        self.emit("    ; Extract hundreds by repeated subtraction")
        self.emit("    ; Example: 234 → subtract 100 twice → hundreds = 2")
        self.emit("    LDA $FB")
        self.emit("    LDX #0           ; X will count hundreds")
        self.emit("output_hundreds:")
        self.emit("    CMP #100")
        self.emit("    BCC output_hundreds_done")
        self.emit("    SBC #100         ; Subtract 100 (carry is set)")
        self.emit("    INX")
        self.emit("    JMP output_hundreds")
        self.emit("output_hundreds_done:")
        self.emit("    STA $FB          ; Save remainder")
        self.emit("    TXA")
        self.emit("    BEQ skip_hundreds ; Skip if zero (suppress leading zero)")
        self.emit("    LDA #0")
        self.emit("    STA $FD          ; Found non-zero, stop suppressing")
        self.emit("    TXA")
        self.emit("    CLC")
        self.emit("    ADC #48          ; Convert to ASCII ('0' = 48)")
        self.emit("    STA $F001        ; Output hundreds digit")
        self.emit("skip_hundreds:")
        self.emit("")
        self.emit("    ; ===== Output tens digit =====")
        self.emit("    ; Extract tens from remainder by repeated subtraction")
        self.emit("    LDA $FB")
        self.emit("    LDX #0           ; X will count tens")
        self.emit("output_tens:")
        self.emit("    CMP #10")
        self.emit("    BCC output_tens_done")
        self.emit("    SBC #10          ; Subtract 10 (carry is set)")
        self.emit("    INX")
        self.emit("    JMP output_tens")
        self.emit("output_tens_done:")
        self.emit("    STA $FB          ; Save remainder (ones digit)")
        self.emit("    TXA")
        self.emit("    BNE print_tens   ; Print if non-zero")
        self.emit("    LDA $FD")
        self.emit("    BNE skip_tens    ; Skip if still suppressing zeros")
        self.emit("print_tens:")
        self.emit("    LDA #0")
        self.emit("    STA $FD          ; Stop suppressing")
        self.emit("    TXA")
        self.emit("    CLC")
        self.emit("    ADC #48          ; Convert to ASCII")
        self.emit("    STA $F001        ; Output tens digit")
        self.emit("skip_tens:")
        self.emit("")
        self.emit("    ; ===== Output ones digit =====")
        self.emit("    ; Always output ones digit, even if zero (e.g., for '0', '10', '100')")
        self.emit("    LDA $FB")
        self.emit("    CLC")
        self.emit("    ADC #48          ; Convert to ASCII")
        self.emit("    STA $F001        ; Output ones digit")
        self.emit("")
        self.emit("    ; Output newline for readability")
        self.emit("    LDA #10")
        self.emit("    STA $F001")
        self.emit("    RTS")
        self.emit("")
        self.emit("input_routine:")
        self.emit("    ; Read multi-digit number from console until Enter")
        self.emit("    ; Reads ASCII digits and converts to binary (0-255 max)")
        self.emit("    ; Uses zero-page $FA for accumulating result")
        self.emit("    ; Algorithm: For each digit, multiply result by 10 and add digit")
        self.emit("    ; Example: '123' → 0*10+1=1, 1*10+2=12, 12*10+3=123")
        self.emit("    LDA #0")
        self.emit("    STA $FA         ; Initialize result to 0")
        self.emit("")
        self.emit("input_loop:")
        self.emit("    ; ===== Wait for next character =====")
        self.emit("input_wait:")
        self.emit("    LDA $F004       ; Poll for input (non-blocking)")
        self.emit("    BEQ input_wait  ; Keep waiting if no key pressed")
        self.emit("")
        self.emit("    ; ===== Check for Enter key =====")
        self.emit("    ; Enter terminates input")
        self.emit("    CMP #10")
        self.emit("    BEQ input_done  ; If Enter (LF), we're done")
        self.emit("    CMP #13")
        self.emit("    BEQ input_done  ; If Enter (CR), we're done")
        self.emit("")
        self.emit("    ; ===== Convert ASCII digit to number =====")
        self.emit("    ; ASCII '0'-'9' are 48-57, so subtract 48")
        self.emit("    SEC")
        self.emit("    SBC #48")
        self.emit("    STA $FE         ; Store new digit in $FE")
        self.emit("")
        self.emit("    ; ===== Multiply current result by 10 =====")
        self.emit("    ; Uses bit shifts: result * 10 = (result * 2 * 5) = (result << 1) * 5")
        self.emit("    ; And: result * 5 = (result << 2) + result")
        self.emit("    ; Combined: result * 10 = ((result << 2) + result) << 1")
        self.emit("    LDA $FA         ; Load current result")
        self.emit("    STA $FD         ; Save copy")
        self.emit("    ASL             ; result * 2")
        self.emit("    ASL             ; result * 4")
        self.emit("    CLC")
        self.emit("    ADC $FD         ; result * 4 + result * 1 = result * 5")
        self.emit("    ASL             ; result * 10")
        self.emit("    CLC")
        self.emit("    ADC $FE         ; Add new digit")
        self.emit("    STA $FA         ; Store updated result")
        self.emit("")
        self.emit("    JMP input_loop  ; Read next character")
        self.emit("")
        self.emit("input_done:")
        self.emit("    LDA $FA         ; Load final result into A")
        self.emit("    RTS")
        self.emit("")
    


def generate_code(ast: Tree, target='generic') -> str:
    """
    Generate 6502 assembly code from an AST.
    
    This is the public API for code generation. It creates a CodeGenerator
    instance and invokes the generation process.
    
    Usage:
        from shared.code_generator import generate_code
        assembly_code = generate_code(ast, target='py65mon')
    
    Args:
        ast: The abstract syntax tree (from semantic analyzer)
        target: Target emulator/platform
                'generic' - Template with placeholder I/O (won't execute)
                'py65mon' - py65mon emulator with console I/O (functional)
        
    Returns:
        String containing complete DASM-format 6502 assembly code
        ready to assemble and run on the target platform
    """
    generator = CodeGenerator(target=target)
    return generator.generate(ast)
