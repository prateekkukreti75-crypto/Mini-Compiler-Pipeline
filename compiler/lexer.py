import re
from typing import List, Tuple, Any

class Token:
    def __init__(self, type: str, value: Any, line: int, col: int):
        self.type = type
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line}, col={self.col})"

class Lexer:
    # Token specifications
    TOKENS = [
        ('FLOAT_CONST', r'\d+\.\d+'),
        ('INT_CONST',   r'\d+'),
        ('STRING_CONST',r'"[^"]*"'),
        ('IF',          r'\bif\b'),
        ('ELSE',        r'\belse\b'),
        ('WHILE',       r'\bwhile\b'),
        ('FOR',         r'\bfor\b'),
        ('FUNC',        r'\bfunc\b'),
        ('RETURN',      r'\breturn\b'),
        ('TRUE',        r'\btrue\b'),
        ('FALSE',       r'\bfalse\b'),
        ('PRINT',       r'\bprint\b'),
        ('TYPE',        r'\b(int|float|string|bool)\b'),
        ('ID',          r'[A-Za-z_][A-Za-z0-9_]*'),
        ('EQ',          r'=='),
        ('NEQ',         r'!='),
        ('LEQ',         r'<='),
        ('GEQ',         r'>='),
        ('AND',         r'&&'),
        ('OR',          r'\|\|'),
        ('NOT',         r'!'),
        ('LT',          r'<'),
        ('GT',          r'>'),
        ('ASSIGN',      r'='),
        ('PLUS',        r'\+'),
        ('MINUS',       r'-'),
        ('COMMENT',     r'//.*'),
        ('MUL',         r'\*'),
        ('DIV',         r'/'),
        ('LPAREN',      r'\('),
        ('RPAREN',      r'\)'),
        ('LBRACE',      r'\{'),
        ('RBRACE',      r'\}'),
        ('SEMI',        r';'),
        ('COMMA',       r','),
        ('WS',          r'[ \t]+'),
        ('NEWLINE',     r'\n'),
    ]

    def __init__(self, text: str):
        self.text = text
        self.tokens: List[Token] = []
        self.line_num = 1
        self.line_start = 0
        self._compile_regex()

    def _compile_regex(self):
        parts = []
        for name, pattern in self.TOKENS:
            parts.append(f'(?P<{name}>{pattern})')
        self.regex = re.compile('|'.join(parts))

    def get_line_text(self, line_num):
        lines = self.text.split('\n')
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return ""

    def tokenize(self) -> List[Token]:
        pos = 0
        while pos < len(self.text):
            match = self.regex.match(self.text, pos)
            if not match:
                col = pos - self.line_start + 1
                line_text = self.get_line_text(self.line_num)
                error_msg = f"Lexical Error at line {self.line_num}, col {col}:\n"
                error_msg += f"{line_text}\n"
                error_msg += " " * (col - 1) + "^"
                raise SyntaxError(error_msg)
            
            type_ = match.lastgroup
            value = match.group(type_)
            col = pos - self.line_start + 1
            
            if type_ == 'NEWLINE':
                self.line_num += 1
                self.line_start = match.end()
            elif type_ == 'COMMENT' or type_ == 'WS':
                pass # ignore whitespace and comments
            else:
                if type_ == 'INT_CONST':
                    value = int(value)
                elif type_ == 'FLOAT_CONST':
                    value = float(value)
                elif type_ == 'STRING_CONST':
                    value = value[1:-1] # Remove quotes
                self.tokens.append(Token(type_, value, self.line_num, col))
            
            pos = match.end()
            
        self.tokens.append(Token('EOF', None, self.line_num, pos - self.line_start + 1))
        return self.tokens

if __name__ == '__main__':
    # Test the lexer
    sample_code = '''
    int a = 10;
    float b = 3.14;
    // This is a comment
    if (a > 5) {
        print(b);
    }
    '''
    lexer = Lexer(sample_code)
    for token in lexer.tokenize():
        print(token)
