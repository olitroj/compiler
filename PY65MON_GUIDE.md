# py65mon Testing Guide

## What is py65mon?

py65mon is a **Python-based 6502 simulator and monitor**. It provides:
- Console-based I/O (text input/output)
- Interactive debugging commands
- Memory inspection and modification
- Step-by-step execution
- Full 6502 instruction support

**Best for:** Debugging, testing logic, step-by-step execution

---

## Installation

py65mon is a Python package. Install it with pip:

```bash
pip install setuptools py65
```

**Requirements:**
- Python 3.x
- DASM assembler (for converting .asm to .bin)

---

## Installing DASM

DASM is needed to assemble the `.asm` files into `.bin` binaries.

### Windows:
1. Download DASM from: https://dasm-assembler.github.io/
2. Extract to a folder (e.g., `C:\dasm\`)
3. Add to PATH or use full path when running

Alternatively, extract to your project folder, and run directly without adding to path using `.\dasm`.

### Linux/Mac:
```bash
# Using Homebrew (Mac)
brew install dasm

# Or download from GitHub
git clone https://github.com/dasm-assembler/dasm.git
cd dasm
make
sudo make install
```

---

## Step-by-Step Tutorial

### Step 1: Compile Your Program

```bash
python src/main.py test_basic.txt --target py65mon
```

This creates `test_basic.asm` with py65mon-optimized assembly code.

### Step 2: Assemble to Binary

Use DASM to convert the assembly file to a binary:

```bash
dasm test_basic.asm -o test_basic.bin -f3
```

**Flags explained:**
- `-o` : Output file name
- `-f3` : Binary format (raw binary)

You should now have `test_basic.bin` in your directory.

### Step 3: Start py65mon

Open a terminal and run:

```bash
py65mon
```

You'll see:

```
Py65 Monitor

PC  AC XR YR SP NV-BDIZC
0000 00 00 00 ff 00110000
.
```

The `.` prompt means py65mon is ready for commands.

### Step 4: Load Your Binary

At the `.` prompt, load your binary at address $0600:

```
. load test_basic.bin 0600
```

**Format:** `load <filename> <address>`

You should see:

```
Wrote +XX bytes from $0600 to $0XXX
```

### Step 5: Run Your Program

Jump to the start address and execute:

```
. goto 0600
```

**Your program will now run!**

For programs with `output()` calls, you'll see the results printed to the console:

```
5
3
8
```

---

## Interactive Debugging Commands

py65mon provides powerful debugging features:

### Memory Commands

**View memory:**
```
. m 0600:0620
```
Shows memory from $0600 to $0620

**View zero-page (variables):**
```
. m 0010:0020
```
Shows your program variables

**Modify memory:**
```
. >0600 A9 05 8D 10 00
```
Write bytes directly to memory

### Execution Commands

**Run from address:**
```
. goto 0600
```
or
```
. g 0600
```

**Step one instruction:**
```
. s
```

**Show registers:**
```
. r
```
Shows current register values

### Disassembly

**Disassemble code:**
```
. d 0600
```
Shows assembly instructions at address

**Disassemble range:**
```
. d 0600:0650
```

### Other Commands

**Show all commands:**
```
. help
```

**Quit:**
```
. quit
```
or Ctrl+C

---

### Register Display

```
PC  AC XR YR SP NV-BDIZC
0603 05 ff 00 fd 00100010
```

- **PC**: Program Counter (current instruction address)
- **AC**: Accumulator
- **XR**: X Register
- **YR**: Y Register
- **SP**: Stack Pointer
- **NV-BDIZC**: Processor status flags

---

## Quick Reference

| Task | Command |
|------|---------|
| **Install** | `pip install setuptools py65` |
| **Compile** | `python src/main.py file.txt --target py65mon` |
| **Assemble** | `dasm file.asm -o file.bin -f3` |
| **Start** | `py65mon` |
| **Load** | `. load file.bin 0600` |
| **Run** | `. goto 0600` |
| **Memory** | `. m 0600:0620` |
| **Disassemble** | `. d 0600` |
| **Help** | `. help` |
| **Quit** | `. quit` or Ctrl+C |