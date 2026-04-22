class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self): return f"Program({self.statements})"

class VarDecl(ASTNode):
    def __init__(self, var_type, var_name, value):
        self.var_type = var_type
        self.var_name = var_name
        self.value = value
    def __repr__(self): return f"VarDecl({self.var_type}, {self.var_name}, {self.value})"

class Assign(ASTNode):
    def __init__(self, var_name, value):
        self.var_name = var_name
        self.value = value
    def __repr__(self): return f"Assign({self.var_name}, {self.value})"

class Print(ASTNode):
    def __init__(self, expr):
        self.expr = expr
    def __repr__(self): return f"Print({self.expr})"

class IfElse(ASTNode):
    def __init__(self, condition, if_body, else_body=None):
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body
    def __repr__(self): return f"IfElse({self.condition}, ...)"

class WhileLoop(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self): return f"While({self.condition}, ...)"

class FunctionDecl(ASTNode):
    def __init__(self, return_type, name, params, body):
        self.return_type = return_type
        self.name = name
        self.params = params  # List of (type, name) tuples
        self.body = body
    def __repr__(self): return f"Function({self.return_type} {self.name}({self.params}))"

class FuncCall(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args
    def __repr__(self): return f"Call({self.name}, {self.args})"

class Return(ASTNode):
    def __init__(self, expr):
        self.expr = expr
    def __repr__(self): return f"Return({self.expr})"

class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self): return f"BinOp({self.left}, '{self.op}', {self.right})"

class LogicalOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self): return f"LogicalOp({self.left}, '{self.op}', {self.right})"

class UnaryOp(ASTNode):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
    def __repr__(self): return f"UnaryOp('{self.op}', {self.expr})"

class Num(ASTNode):
    def __init__(self, value, num_type):
        self.value = value
        self.num_type = num_type
    def __repr__(self): return f"Num({self.value})"

class StringVal(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self): return f"String({self.value})"

class BoolVal(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self): return f"Bool({self.value})"

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name
    def __repr__(self): return f"Id({self.name})"
