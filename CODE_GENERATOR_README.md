# 6502 Code Generator

This code generator compiles your custom language into DASM assembly for the 6502 microprocessor.

## Overview

The code generator takes an Abstract Syntax Tree (AST) produced by the semantic analyzer and generates valid 6502 assembly code that can be assembled with DASM.

## Features

### Supported Language Constructs

1. **Variable Declaration and Assignment**
   ```
   var x = 10;
   x = x + 5;
   ```

2. **Arithmetic Operators**
   - Addition: `+`
   - Subtraction: `-` (binary and unary)
   
3. **Bitwise Operators**
   - AND: `&`
   - OR: `|`
   - XOR: `^`
   - NOT: `~`

4. **Logical Operators**
   - AND: `&&`
   - OR: `||`
   - XOR: `^^`
   - NOT: `!`

5. **Comparison Operators**
   - Less than: `<`
   - Less than or equal: `<=`
   - Greater than: `>`
   - Greater than or equal: `>=`
   - Equal: `==`
   - Not equal: `!=`

6. **Shift Operators**
   - Left shift: `<<`
   - Right shift: `>>`

7. **Control Flow**
   - If/else statements
   ```
   if (x < y) {
       x = x + 1;
   } else {
       y = y + 1;
   };
   ```

8. **Loops**
   - While loops
   ```
   while (x > 0) {
       x--;
   };
   ```
   
   - Do-while loops
   ```
   do {
       x--;
   } while (x > 0);
   ```

9. **Increment/Decrement**
   - Post-increment: `x++`
   - Post-decrement: `x--`

10. **I/O Functions**
    - `input()` - Read from input port
    - `output(value)` - Write to output port

## Memory Layout

The generated code uses the following memory layout:

- **Zero Page ($10-$FF)**: Variables are allocated starting at $10
- **$FE**: Temporary storage for binary operations
- **$0200+**: Expression evaluation stack (using 6502 hardware stack)
- **$0600**: Program start address
- **$D010**: Input port (memory-mapped I/O)
- **$D012**: Output port (memory-mapped I/O)

## 6502 Instructions Used

The code generator uses only standard 6502 instructions:

### Load/Store
- `LDA` - Load Accumulator
- `STA` - Store Accumulator
- `LDX` - Load X Register
- `TXS` - Transfer X to Stack Pointer
- `TAX` - Transfer A to X
- `TAY` - Transfer A to Y
- `TYA` - Transfer Y to A

### Stack Operations
- `PHA` - Push Accumulator
- `PLA` - Pull Accumulator

### Arithmetic/Logic
- `ADC` - Add with Carry
- `SBC` - Subtract with Carry
- `AND` - Logical AND
- `ORA` - Logical OR (Inclusive)
- `EOR` - Exclusive OR
- `ASL` - Arithmetic Shift Left
- `LSR` - Logical Shift Right
- `INC` - Increment Memory
- `DEC` - Decrement Memory
- `DEX` - Decrement X
- `CMP` - Compare with Accumulator
- `CPX` - Compare with X

### Flags
- `CLC` - Clear Carry Flag
- `SEC` - Set Carry Flag

### Branches
- `BEQ` - Branch if Equal
- `BNE` - Branch if Not Equal
- `BCC` - Branch if Carry Clear (less than)
- `BCS` - Branch if Carry Set (greater than or equal)

### Control
- `JMP` - Jump
- `JSR` - Jump to Subroutine
- `RTS` - Return from Subroutine
- `BRK` - Break (end program)

## Usage

```bash
python src/main.py <source_file>
```

The compiler will generate `<source_file>.asm` containing the 6502 assembly code.

## Expression Evaluation

Expressions are evaluated using post-order traversal:

1. Traverse to leaf nodes (literals and variables)
2. Load values into the accumulator
3. For binary operators:
   - Evaluate left operand
   - Push result on stack
   - Evaluate right operand  
   - Pop left operand
   - Apply operator
4. Result is left in accumulator A

This approach correctly handles operator precedence as the AST is already structured with precedence in mind.

## Limitations

1. **8-bit values only**: The 6502 is an 8-bit processor
2. **Limited variable space**: Zero page provides 240 bytes (excluding system area)
3. **No multiplication/division**: Must be implemented in software if needed
4. **I/O is system-dependent**: Memory-mapped I/O addresses are examples
