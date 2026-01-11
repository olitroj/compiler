from shared.tok import Token, TokenType

class LexerError(Exception):
    """Exception raised for lexical analysis errors"""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer Error at line {line}, column {column}: {message}")

class Lexer:
    """
    Lexical analyzer that converts source code into a stream of tokens.
    """
    
    # Keywords mapping for quick lookup
    KEYWORDS = {
        "var": TokenType.VAR,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "while": TokenType.WHILE,
        "do": TokenType.DO,
    }
    
    def __init__(self, source: str):
        """
        Initialize the lexer with source code.
        
        Args:
            source: The source code string to tokenize
        """
        self.source = source
        self.pos = 0        # Current position in source
        self.line = 1       # Current line number
        self.column = 1     # Current column number
        self.tokens = []    # List of generated tokens
    
    def current_char(self) -> str | None:
        """Return the current character without advancing, or None if at end"""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek(self, offset: int = 1) -> str | None:
        """
        Look ahead at a character without consuming it.
        
        Args:
            offset: How many characters ahead to peek (default 1)
        
        Returns:
            The character at pos+offset, or None if beyond end
        """
        peek_pos = self.pos + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def advance(self) -> str | None:
        """
        Consume and return the current character, advancing position.
        Updates line and column tracking.
        """
        if self.pos >= len(self.source):
            return None
        
        char = self.source[self.pos]
        self.pos += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def skip_whitespace(self):
        """Skip whitespace characters (space, tab, newline, carriage return)"""
        while self.current_char() and self.current_char() in ' \t\n\r':
            self.advance()
    
    def skip_comment(self):
        """
        Skip single-line comments (// ...) and multi-line comments (/* ... */)
        Returns True if a comment was skipped, False otherwise
        """
        if self.current_char() == '/' and self.peek() == '/':
            # Single-line comment
            while self.current_char() and self.current_char() != '\n':
                self.advance()
            return True
        
        elif self.current_char() == '/' and self.peek() == '*':
            # Multi-line comment
            start_line = self.line
            self.advance()  # consume '/'
            self.advance()  # consume '*'
            
            while True:
                if self.current_char() is None:
                    raise LexerError(f"Unterminated comment starting at line {start_line}", 
                                   self.line, self.column)
                
                if self.current_char() == '*' and self.peek() == '/':
                    self.advance()  # consume '*'
                    self.advance()  # consume '/'
                    break
                
                self.advance()
            
            return True
        
        return False
    
    def read_identifier(self) -> str:
        """
        Read an identifier or keyword.
        Identifiers start with a letter or underscore, followed by letters, digits, or underscores.
        """
        start_pos = self.pos
        
        # First character must be letter or underscore
        if not (self.current_char().isalpha() or self.current_char() == '_'):
            raise LexerError(f"Invalid identifier start: '{self.current_char()}'", 
                           self.line, self.column)
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            self.advance()
        
        return self.source[start_pos:self.pos]
    
    def read_number(self) -> int:
        """
        Read a numeric literal (integer).
        Supports decimal numbers.
        """
        start_pos = self.pos
        
        while self.current_char() and self.current_char().isdigit():
            self.advance()
        
        return int(self.source[start_pos:self.pos])
    
    def tokenize(self) -> list[Token]:
        """
        Main method to tokenize the entire source code.
        
        Returns:
            List of Token objects
        
        Raises:
            LexerError: If invalid characters or malformed tokens are encountered
        """
        self.tokens = []
        
        while self.pos < len(self.source):
            # Skip whitespace and comments
            self.skip_whitespace()
            
            if self.current_char() is None:
                break
            
            if self.skip_comment():
                continue
            
            # Save position for error reporting
            token_line = self.line
            token_column = self.column
            char = self.current_char()
            
            # Identifiers and keywords
            if char.isalpha() or char == '_':
                identifier = self.read_identifier()
                # Check if it's a keyword
                if identifier in self.KEYWORDS:
                    self.tokens.append(Token(self.KEYWORDS[identifier]))
                else:
                    self.tokens.append(Token(TokenType.ID, identifier))
            
            # Numeric literals
            elif char.isdigit():
                number = self.read_number()
                self.tokens.append(Token(TokenType.LITERAL, number))
            
            # Operators and punctuation (multi-character operators first!)
            elif char == '+':
                self.advance()
                if self.current_char() == '+':
                    self.advance()
                    self.tokens.append(Token(TokenType.INCREMENT))
                else:
                    self.tokens.append(Token(TokenType.PLUS))
            
            elif char == '-':
                self.advance()
                if self.current_char() == '-':
                    self.advance()
                    self.tokens.append(Token(TokenType.DECREMENT))
                else:
                    self.tokens.append(Token(TokenType.MINUS))
            
            elif char == '&':
                self.advance()
                if self.current_char() == '&':
                    self.advance()
                    self.tokens.append(Token(TokenType.LOGIC_AND))
                else:
                    self.tokens.append(Token(TokenType.BIT_AND))
            
            elif char == '|':
                self.advance()
                if self.current_char() == '|':
                    self.advance()
                    self.tokens.append(Token(TokenType.LOGIC_OR))
                else:
                    self.tokens.append(Token(TokenType.BIT_OR))
            
            elif char == '^':
                self.advance()
                if self.current_char() == '^':
                    self.advance()
                    self.tokens.append(Token(TokenType.LOGIC_XOR))
                else:
                    self.tokens.append(Token(TokenType.BIT_XOR))
            
            elif char == '<':
                self.advance()
                if self.current_char() == '<':
                    self.advance()
                    self.tokens.append(Token(TokenType.SHIFT_LEFT))
                elif self.current_char() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.LESS_THAN_EQUALS))
                else:
                    self.tokens.append(Token(TokenType.LESS_THAN))
            
            elif char == '>':
                self.advance()
                if self.current_char() == '>':
                    self.advance()
                    self.tokens.append(Token(TokenType.SHIFT_RIGHT))
                elif self.current_char() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.GREATER_THAN_EQUALS))
                else:
                    self.tokens.append(Token(TokenType.GREATER_THAN))
            
            elif char == '=':
                self.advance()
                if self.current_char() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.EQUAL))
                else:
                    self.tokens.append(Token(TokenType.ASSIGN))
            
            elif char == '!':
                self.advance()
                if self.current_char() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.NOT_EQUAL))
                else:
                    self.tokens.append(Token(TokenType.LOGIC_NOT))
            
            # Single-character tokens
            elif char == '~':
                self.advance()
                self.tokens.append(Token(TokenType.BIT_NOT))
            
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.OPEN_BRACE))
            
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.CLOSE_BRACE))
            
            elif char == '{':
                self.advance()
                self.tokens.append(Token(TokenType.OPEN_CURLY))
            
            elif char == '}':
                self.advance()
                self.tokens.append(Token(TokenType.CLOSE_CURLY))
            
            elif char == ';':
                self.advance()
                self.tokens.append(Token(TokenType.SEMICOLON))
            
            elif char == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA))
            
            else:
                raise LexerError(f"Unexpected character: '{char}'", token_line, token_column)
        
        return self.tokens
    
    def __repr__(self) -> str:
        """String representation showing all tokens"""
        return f"Lexer(tokens={len(self.tokens)}, current_pos={self.pos})"
