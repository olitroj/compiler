# Custom Language to 6502 Compiler

A compiler that translates a custom high-level language into 6502 microprocessor assembly code (DASM syntax).

## Features

- Complete lexer, parser, and semantic analyzer
- Expression evaluation with full operator support
- Control flow (if/else, while, do-while)
- Variable declarations and assignments
- I/O operations (input/output)
- 6502 assembly code generation

## Quick Start

### 1. Write Your Program

Create a text file with your source code:

```javascript
var x = 10;
var y = 5;
var sum = x + y;
output(sum);
```

### 2. Compile

```bash
# For generic 6502 code
python src/main.py my_program.txt

# For py65mon emulator
python src/main.py my_program.txt --target py65mon
```

### 3. Run

**Option A: Generic 6502 Code**
- Compile without any targets
- Assemble: `dasm my_program.asm -o my_program.bin -f3`
- Upload to a 6502 processor

**Option B: py65mon**
- Install: `pip install setuptools py65`
- Compile with `--target py65mon`
- Assemble: `dasm my_program.asm -o my_program.bin -f3`
- Run: `py65mon` then `load my_program.bin 0600` then `goto 0600`
- Any lines with `output();` will print the value stored in the variable to the screen.

## Language Features

### Variables
```javascript
var x = 10;
var y = 5;
x = x + 3;
```

### Operators
```javascript
// Arithmetic
result = x + y;
result = x - y;
result = -x;
x++;
x--;

// Bitwise
result = x & y;   // AND
result = x | y;   // OR
result = x ^ y;   // XOR
result = ~x;      // NOT
result = x << 2;  // Left shift
result = x >> 1;  // Right shift

// Logical
result = x && y;  // AND
result = x || y;  // OR
result = x ^^ y;  // XOR
result = !x;      // NOT

// Comparison
result = x < y;
result = x <= y;
result = x > y;
result = x >= y;
result = x == y;
result = x != y;
```

### Control Flow
```javascript
// If/Else
if (x > 0) {
    output(x);
} else {
    output(0);
};

// While Loop
while (x > 0) {
    x--;
};

// Do-While Loop
do {
    x++;
} while (x < 10);
```

### I/O
```javascript
var value = input();  // Read input
output(value);        // Write output (displays as unsigned 0-255)
```

**Note:** All values are 8-bit (0-255). The `output()` function displays values as unsigned integers. Negative numbers in two's complement (e.g., `-12` = `244`) will display as their unsigned equivalent.

## Example Programs

Example programs are found in `test/`.

- `Test Basic` is a basic test with minimal functionality to test assembly code generation and execution.

- `Test Program` is a more comprehensive test showcasing the languages capabilities.

- `Test IO` tests input and output functions.

- `Test Complex` tests a complex expression.

- `Test Num Guess` is a simple number guessing game. If the input is too small, 0 is printed, and it waits for another input.
  If the guess is too large, 2 is printed. If the guess matches the answer, 1 is printed and the game finished.

## Architecture

- **Lexer** (`src/shared/lexer.py`) - Tokenizes source code
- **Parser** (`src/syntax/parser.py`) - Builds parse tree
- **Semantic Analyzer** (`src/semantics/sem.py`) - Validates and transforms to AST
- **Code Generator** (`src/shared/code_generator.py`) - Generates 6502 assembly

## Generated Code Details

- **Target**: 6502 microprocessor
- **Syntax**: DASM assembler format
- **Start Address**: `$0600`
- **Variables**: Zero-page memory (`$10-$FF`)
- **Stack**: Hardware stack for expression evaluation
- **I/O**: Configurable per emulator target

## Requirements

- Python 3.x (for compiler)
- DASM (for assembling to binary)
- py65mon (for testing)
