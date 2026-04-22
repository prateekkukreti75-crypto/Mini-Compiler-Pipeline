from .ast_nodes import *

class IRGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def generate(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No IR generation for {type(node).__name__}")

    def visit_Program(self, node):
        for stmt in node.statements:
            self.generate(stmt)
        return self.instructions

    def visit_FunctionDecl(self, node):
        l_end_func = self.new_label()
        self.instructions.append(('GOTO', l_end_func))
        self.instructions.append(('LABEL', f"FUNC_{node.name}"))
        for param_type, param_name in reversed(node.params):
            self.instructions.append(('PARAM_POP', param_name))
        for stmt in node.body:
            self.generate(stmt)
        self.instructions.append(('RETURN_VOID',))
        self.instructions.append(('LABEL', l_end_func))

    def visit_Return(self, node):
        val = self.generate(node.expr)
        self.instructions.append(('RETURN', val))

    def visit_FuncCall(self, node):
        for arg in node.args:
            val = self.generate(arg)
            self.instructions.append(('PARAM_PUSH', val))
        temp = self.new_temp()
        self.instructions.append(('CALL', node.name, len(node.args), temp))
        return temp

    def visit_VarDecl(self, node):
        val = self.generate(node.value)
        self.instructions.append(('ASSIGN', val, node.var_name))

    def visit_Assign(self, node):
        val = self.generate(node.value)
        self.instructions.append(('ASSIGN', val, node.var_name))

    def visit_Print(self, node):
        val = self.generate(node.expr)
        self.instructions.append(('PRINT', val))

    def visit_IfElse(self, node):
        cond = self.generate(node.condition)
        l_true = self.new_label()
        l_end = self.new_label()
        
        if node.else_body:
            l_false = self.new_label()
            self.instructions.append(('IF_FALSE_GOTO', cond, l_false))
        else:
            self.instructions.append(('IF_FALSE_GOTO', cond, l_end))
        
        self.instructions.append(('LABEL', l_true))
        for stmt in node.if_body:
            self.generate(stmt)
        
        if node.else_body:
            self.instructions.append(('GOTO', l_end))
            self.instructions.append(('LABEL', l_false))
            for stmt in node.else_body:
                self.generate(stmt)
        
        self.instructions.append(('LABEL', l_end))

    def visit_WhileLoop(self, node):
        l_start = self.new_label()
        l_end = self.new_label()
        
        self.instructions.append(('LABEL', l_start))
        cond = self.generate(node.condition)
        self.instructions.append(('IF_FALSE_GOTO', cond, l_end))
        
        for stmt in node.body:
            self.generate(stmt)
            
        self.instructions.append(('GOTO', l_start))
        self.instructions.append(('LABEL', l_end))

    def visit_LogicalOp(self, node):
        left = self.generate(node.left)
        right = self.generate(node.right)
        temp = self.new_temp()
        self.instructions.append((node.op, left, right, temp))
        return temp

    def visit_UnaryOp(self, node):
        val = self.generate(node.expr)
        temp = self.new_temp()
        self.instructions.append((node.op, val, temp))
        return temp

    def visit_BinOp(self, node):
        left = self.generate(node.left)
        right = self.generate(node.right)
        temp = self.new_temp()
        self.instructions.append((node.op, left, right, temp))
        return temp

    def visit_Num(self, node):
        return node.value

    def visit_StringVal(self, node):
        return f'"{node.value}"'

    def visit_BoolVal(self, node):
        return 1 if node.value else 0

    def visit_Identifier(self, node):
        return node.name
