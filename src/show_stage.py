from shared.lexer import Lexer, LexerError
from syntax.parser import parse
from semantics.sem import check_semantics
from shared.code_generator import generate_code
import sys
import argparse
import os

# Increase recursion limit for parsing larger programs
# Default is 1000, which is insufficient for programs with many statements
sys.setrecursionlimit(5000)

def tokenize_from_file(filepath: str):
    """
    Read source code from a file and tokenize it.
    
    Args:
        filepath: Path to the source code file
    """
    try:
        # Read the file contents
        with open(filepath, 'r', encoding='utf-8') as file:
            source_code = file.read()
        
        # Create lexer and tokenize
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        return tokens
        
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found!")
        return None
    except PermissionError:
        print(f"Error: Permission denied reading '{filepath}'!")
        return None
    except LexerError as e:
        print(f"Lexer Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def tokenize_from_string(source_code: str):
    """
    Tokenize source code from a string.
    
    Args:
        source_code: The source code string
    """
    try:
        # Create lexer instance and tokenize
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # Print the tokens
        print(f"Successfully tokenized {len(tokens)} tokens:\n")
        for i, token in enumerate(tokens, 1):
            print(f"{i:3d}. {token}")
        
        return tokens
        
    except LexerError as e:
        print(f"Lexer Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Compile custom language to 6502 assembly',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/show_stage.py                                # Run default test/test_basic.txt with py65mon target
  python src/show_stage.py program.txt                    # Compile with py65mon target
  python src/show_stage.py program.txt --stage lexer      # Stop after lexer, and output.
        """
    )
    parser.add_argument('file', nargs='?', help='Source code file to compile (default: test/test_basic.txt)')
    parser.add_argument('--stage', choices=['lexer', 'parser', 'semantics', 'assembly'], 
                       help='Stage to stop at (default: assembly)')
    
    args = parser.parse_args()
    
    # Check if a file path was provided
    if args.file:
        filepath = args.file
    else:
        filepath = os.path.join(os.path.dirname(__file__), 'test', 'test_basic.txt')
        print(f"Using default test file: {filepath}")

    toks = tokenize_from_file(filepath)
    
    if toks is None:
        return
    
    if args.stage == 'lexer':
        print(f"Successfully tokenized {len(toks)} tokens:\n")
        for i, token in enumerate(toks, 1):
            print(f"{i:3d}. {token}")
        return
    
    # Parse the tokens into an AST
    tree = parse(toks)

    if args.stage == 'parser':
        print(f"Parse tree: {tree}")
        return
    
    # Check semantics
    semantics_valid = check_semantics(tree)
    print(f"Semantic analysis: {semantics_valid}")
    
    if not semantics_valid:
        print("Error: Semantic analysis failed!")
        return
    
    if args.stage == 'semantics':
        return
    
    # Generate assembly code with target emulator
    target = 'py65mon'
    print(f"\nGenerating 6502 assembly code (target: {target})...")
    asm_code = generate_code(tree, target=target)
    
    # Write assembly to output file
    output_file = filepath.rsplit('.', 1)[0] + '.asm'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(asm_code)
    
    print(f"Assembly code written to: {output_file}")
    print("\n" + "="*60)
    print(asm_code)
    print("="*60)
        
        
if __name__ == "__main__":
    main()
