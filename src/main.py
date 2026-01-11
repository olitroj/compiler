from shared.lexer import Lexer, LexerError
import sys

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
        
        print(f"Reading from: {filepath}")
        print(f"Source code length: {len(source_code)} characters\n")
        print("=" * 60)
        print(source_code)
        print("=" * 60)
        print()
        
        # Create lexer and tokenize
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # Print the tokens
        print(f"Successfully tokenized {len(tokens)} tokens:\n")
        for i, token in enumerate(tokens, 1):
            print(f"{i:3d}. {token}")
        
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
    # Check if a file path was provided as command line argument
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        tokenize_from_file(filepath)
    else:
        # Default: use example string
        print("No file specified. Using example source code.")
        print("Usage: python main.py <source_file>")
        print()
        
        source_code = """
        var x = 10;
        var y = 20;
        
        if (x < y) {
            x = x + 1;
            y++;
        }
        
        while (x <= y) {
            x = x << 1;
        }
        
        // This is a comment
        var result = (x && y) || (x ^^ y);
        
        /* Multi-line
           comment test */
        do {
            x--;
        } while (x != 0);
        """
        
        tokenize_from_string(source_code)

if __name__ == "__main__":
    main()
