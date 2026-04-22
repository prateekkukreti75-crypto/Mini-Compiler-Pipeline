from .ast_nodes import *

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]
    
    def enter_scope(self):
        self.scopes.append({})
        
    def exit_scope(self):
        self.scopes.pop()
        
    def declare(self, name, var_type):
        if name in self.scopes[-1]:
            raise Exception(f"Semantic Error: '{name}' already declared in current scope.")
        self.scopes[-1][name] = var_type
        
    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_function_return_type = None

    def analyze(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{type(node).__name__} method in SemanticAnalyzer")

    def visit_Program(self, node):
        for stmt in node.statements:
            self.analyze(stmt)

    def visit_FunctionDecl(self, node):
        self.symbol_table.declare(node.name, f"func_{node.return_type}")
        self.symbol_table.enter_scope()
        self.current_function_return_type = node.return_type
        for ptype, pname in node.params:
            self.symbol_table.declare(pname, ptype)
        for stmt in node.body:
            self.analyze(stmt)
        self.current_function_return_type = None
        self.symbol_table.exit_scope()

    def visit_Return(self, node):
        if not self.current_function_return_type:
            raise Exception("Semantic Error: Return statement outside of function.")
        expr_type = self.analyze(node.expr)
        if self.current_function_return_type != 'void' and expr_type != self.current_function_return_type:
            print(f"Warning: Returning {expr_type} in function returning {self.current_function_return_type}")
        return expr_type

    def visit_FuncCall(self, node):
        func_type = self.symbol_table.lookup(node.name)
        if not func_type or not func_type.startswith("func_"):
            raise Exception(f"Semantic Error: Function '{node.name}' not declared.")
        for arg in node.args:
            self.analyze(arg)
        return func_type.split('_')[1]

    def visit_VarDecl(self, node):
        expr_type = self.analyze(node.value)
        if node.var_type == 'int' and expr_type == 'float':
            print(f"Warning: Assigning float to int variable '{node.var_name}'.")
        self.symbol_table.declare(node.var_name, node.var_type)
        return node.var_type

    def visit_Assign(self, node):
        var_type = self.symbol_table.lookup(node.var_name)
        if not var_type:
            raise Exception(f"Semantic Error: Variable '{node.var_name}' not declared.")
        expr_type = self.analyze(node.value)
        if var_type == 'int' and expr_type == 'float':
            print(f"Warning: Assigning float to int variable '{node.var_name}'.")

    def visit_Print(self, node):
        self.analyze(node.expr)

    def visit_IfElse(self, node):
        cond_type = self.analyze(node.condition)
        self.symbol_table.enter_scope()
        for stmt in node.if_body:
            self.analyze(stmt)
        self.symbol_table.exit_scope()
        
        if node.else_body:
            self.symbol_table.enter_scope()
            for stmt in node.else_body:
                self.analyze(stmt)
            self.symbol_table.exit_scope()

    def visit_WhileLoop(self, node):
        cond_type = self.analyze(node.condition)
        self.symbol_table.enter_scope()
        for stmt in node.body:
            self.analyze(stmt)
        self.symbol_table.exit_scope()

    def visit_LogicalOp(self, node):
        self.analyze(node.left)
        self.analyze(node.right)
        return 'bool'

    def visit_UnaryOp(self, node):
        return self.analyze(node.expr)

    def visit_BinOp(self, node):
        left_type = self.analyze(node.left)
        right_type = self.analyze(node.right)
        
        if node.op in ('<', '>', '<=', '>=', '==', '!='):
            return 'bool'
            
        if left_type == 'float' or right_type == 'float':
            return 'float'
        if left_type == 'string' or right_type == 'string':
            if node.op == '+': return 'string'
            raise Exception("Semantic Error: Invalid operation on string.")
        return 'int'

    def visit_Num(self, node):
        return node.num_type

    def visit_StringVal(self, node):
        return 'string'

    def visit_BoolVal(self, node):
        return 'bool'

    def visit_Identifier(self, node):
        var_type = self.symbol_table.lookup(node.name)
        if not var_type:
            raise Exception(f"Semantic Error: Variable '{node.name}' not declared.")
        return var_type
