from .lexer import Lexer, Token
from .ast_nodes import *

class Parser:
    def __init__(self, tokens, lexer_instance=None):
        self.tokens = tokens
        self.lexer = lexer_instance
        self.pos = 0
        self.current_token = self.tokens[self.pos]

    def error(self, expected_type=None):
        token = self.current_token
        msg = f"Syntax Error at line {token.line}, col {token.col}:\n"
        if self.lexer:
            line_text = self.lexer.get_line_text(token.line)
            msg += f"{line_text}\n"
            msg += " " * (token.col - 1) + "^\n"
        
        if expected_type:
            msg += f"Expected {expected_type}, got {token.type}"
        else:
            msg += f"Invalid syntax, got {token.type}"
        raise SyntaxError(msg)

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
        else:
            self.error(token_type)

    def parse(self):
        statements = []
        while self.current_token.type != 'EOF':
            statements.append(self.top_level_decl())
        return Program(statements)

    def top_level_decl(self):
        if self.current_token.type == 'FUNC':
            return self.function_decl()
        return self.statement()

    def function_decl(self):
        self.eat('FUNC')
        name = self.current_token.value
        self.eat('ID')
        self.eat('LPAREN')
        params = []
        if self.current_token.type == 'TYPE':
            ptype = self.current_token.value
            self.eat('TYPE')
            pname = self.current_token.value
            self.eat('ID')
            params.append((ptype, pname))
            while self.current_token.type == 'COMMA':
                self.eat('COMMA')
                ptype = self.current_token.value
                self.eat('TYPE')
                pname = self.current_token.value
                self.eat('ID')
                params.append((ptype, pname))
        self.eat('RPAREN')
        
        # Optional return type (e.g. func foo() int { })
        return_type = "void"
        if self.current_token.type == 'TYPE':
            return_type = self.current_token.value
            self.eat('TYPE')
            
        self.eat('LBRACE')
        body = self.block()
        self.eat('RBRACE')
        return FunctionDecl(return_type, name, params, body)

    def statement(self):
        if self.current_token.type == 'TYPE':
            return self.var_decl()
        elif self.current_token.type == 'ID':
            # Could be assignment or function call
            next_type = self.tokens[self.pos + 1].type if self.pos + 1 < len(self.tokens) else None
            if next_type == 'LPAREN':
                call = self.func_call()
                self.eat('SEMI')
                return call
            return self.assignment()
        elif self.current_token.type == 'PRINT':
            return self.print_statement()
        elif self.current_token.type == 'IF':
            return self.if_statement()
        elif self.current_token.type == 'WHILE':
            return self.while_statement()
        elif self.current_token.type == 'RETURN':
            return self.return_statement()
        else:
            self.error()

    def return_statement(self):
        self.eat('RETURN')
        expr = self.expr()
        self.eat('SEMI')
        return Return(expr)

    def func_call(self):
        name = self.current_token.value
        self.eat('ID')
        self.eat('LPAREN')
        args = []
        if self.current_token.type != 'RPAREN':
            args.append(self.expr())
            while self.current_token.type == 'COMMA':
                self.eat('COMMA')
                args.append(self.expr())
        self.eat('RPAREN')
        return FuncCall(name, args)

    def var_decl(self):
        var_type = self.current_token.value
        self.eat('TYPE')
        var_name = self.current_token.value
        self.eat('ID')
        self.eat('ASSIGN')
        expr = self.expr()
        self.eat('SEMI')
        return VarDecl(var_type, var_name, expr)

    def assignment(self):
        var_name = self.current_token.value
        self.eat('ID')
        self.eat('ASSIGN')
        expr = self.expr()
        self.eat('SEMI')
        return Assign(var_name, expr)

    def print_statement(self):
        self.eat('PRINT')
        self.eat('LPAREN')
        expr = self.expr()
        self.eat('RPAREN')
        self.eat('SEMI')
        return Print(expr)

    def if_statement(self):
        self.eat('IF')
        self.eat('LPAREN')
        condition = self.expr()
        self.eat('RPAREN')
        self.eat('LBRACE')
        if_body = self.block()
        self.eat('RBRACE')
        else_body = None
        if self.current_token.type == 'ELSE':
            self.eat('ELSE')
            self.eat('LBRACE')
            else_body = self.block()
            self.eat('RBRACE')
        return IfElse(condition, if_body, else_body)

    def while_statement(self):
        self.eat('WHILE')
        self.eat('LPAREN')
        condition = self.expr()
        self.eat('RPAREN')
        self.eat('LBRACE')
        body = self.block()
        self.eat('RBRACE')
        return WhileLoop(condition, body)

    def block(self):
        statements = []
        while self.current_token.type not in ('RBRACE', 'EOF'):
            statements.append(self.statement())
        return statements

    def expr(self):
        return self.logical_or()

    def logical_or(self):
        node = self.logical_and()
        while self.current_token.type == 'OR':
            op = self.current_token.value
            self.eat('OR')
            node = LogicalOp(node, op, self.logical_and())
        return node

    def logical_and(self):
        node = self.equality()
        while self.current_token.type == 'AND':
            op = self.current_token.value
            self.eat('AND')
            node = LogicalOp(node, op, self.equality())
        return node

    def equality(self):
        node = self.relational()
        while self.current_token.type in ('EQ', 'NEQ'):
            op = self.current_token.value
            self.eat(self.current_token.type)
            node = BinOp(node, op, self.relational())
        return node

    def relational(self):
        node = self.term()
        while self.current_token.type in ('LT', 'GT', 'LEQ', 'GEQ'):
            op = self.current_token.value
            self.eat(self.current_token.type)
            node = BinOp(node, op, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current_token.type in ('PLUS', 'MINUS'):
            op = self.current_token.value
            self.eat(self.current_token.type)
            node = BinOp(node, op, self.factor())
        return node

    def factor(self):
        node = self.unary()
        while self.current_token.type in ('MUL', 'DIV'):
            op = self.current_token.value
            self.eat(self.current_token.type)
            node = BinOp(node, op, self.unary())
        return node

    def unary(self):
        token = self.current_token
        if token.type in ('MINUS', 'NOT'):
            self.eat(token.type)
            return UnaryOp(token.value, self.unary())
        return self.primary()

    def primary(self):
        token = self.current_token
        if token.type == 'INT_CONST':
            self.eat('INT_CONST')
            return Num(token.value, 'int')
        elif token.type == 'FLOAT_CONST':
            self.eat('FLOAT_CONST')
            return Num(token.value, 'float')
        elif token.type == 'STRING_CONST':
            self.eat('STRING_CONST')
            return StringVal(token.value)
        elif token.type == 'TRUE':
            self.eat('TRUE')
            return BoolVal(True)
        elif token.type == 'FALSE':
            self.eat('FALSE')
            return BoolVal(False)
        elif token.type == 'ID':
            # Check if func call
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].type == 'LPAREN':
                return self.func_call()
            else:
                self.eat('ID')
                return Identifier(token.value)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.expr()
            self.eat('RPAREN')
            return node
        else:
            self.error()
