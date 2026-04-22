class Optimizer:
    def __init__(self, instructions):
        self.instructions = instructions

    def optimize(self):
        # We will run passes until the code stops changing
        changed = True
        while changed:
            original = list(self.instructions)
            self.constant_folding()
            self.constant_propagation()
            self.copy_propagation()
            self.common_subexpression_elimination()
            self.dead_code_elimination()
            if self.instructions == original:
                changed = False
        return self.instructions

    def common_subexpression_elimination(self):
        """ Replaces recomputed expressions with previously computed temporaries. """
        expressions = {}
        new_instructions = []
        for instr in self.instructions:
            if len(instr) == 4 and instr[0] not in ('CALL',): # It's a binary operation
                op, left, right, result = instr
                expr = (op, left, right)
                if expr in expressions:
                    # Replace with ASSIGN to previous temporary
                    new_instructions.append(('ASSIGN', expressions[expr], result))
                else:
                    expressions[expr] = result
                    new_instructions.append(instr)
            elif instr[0] in ('LABEL', 'FUNC'): # Clear expressions map across blocks/functions
                expressions.clear()
                new_instructions.append(instr)
            else:
                if instr[0] == 'ASSIGN':
                    # If variable gets reassigned, any expression using it might be invalid
                    # For simplicity, we just clear expressions if ANY variable is reassigned
                    val, result = instr[1], instr[2]
                    if not result.startswith('t'):
                        expressions.clear()
                new_instructions.append(instr)
        self.instructions = new_instructions

    def is_number(self, val):
        return isinstance(val, (int, float))

    def evaluate(self, op, left, right):
        if op == '+': return left + right
        if op == '-': return left - right
        if op == '*': return left * right
        if op == '/': return left / right if right != 0 else None
        if op == '==': return int(left == right)
        if op == '!=': return int(left != right)
        if op == '<': return int(left < right)
        if op == '>': return int(left > right)
        if op == '<=': return int(left <= right)
        if op == '>=': return int(left >= right)
        return None

    def constant_folding(self):
        """ Evaluates expressions with constant operands at compile time. """
        new_instructions = []
        for instr in self.instructions:
            if len(instr) == 4:
                op, left, right, result = instr
                if self.is_number(left) and self.is_number(right):
                    val = self.evaluate(op, left, right)
                    if val is None:
                        new_instructions.append(instr)
                    else:
                        new_instructions.append(('ASSIGN', val, result))
                else:
                    new_instructions.append(instr)
            else:
                new_instructions.append(instr)
        self.instructions = new_instructions

    def constant_propagation(self):
        """ Propagates constant values to their usages. """
        constants = {}
        new_instructions = []
        for instr in self.instructions:
            if instr[0] == 'LABEL':
                constants.clear()
                new_instructions.append(instr)
            elif instr[0] == 'ASSIGN':
                val, result = instr[1], instr[2]
                if val in constants:
                    val = constants[val]
                
                if self.is_number(val) or (isinstance(val, str) and val.startswith('"')):
                    constants[result] = val
                else:
                    # If variable is reassigned to a non-constant, remove it from constants
                    if result in constants:
                        del constants[result]
                new_instructions.append(('ASSIGN', val, result))
            else:
                new_instr = list(instr)
                # Replace uses of constants
                for i in range(1, len(new_instr)):
                    if new_instr[i] in constants:
                        new_instr[i] = constants[new_instr[i]]
                new_instructions.append(tuple(new_instr))
        self.instructions = new_instructions

    def copy_propagation(self):
        """ If a = b, replaces uses of a with b. """
        copies = {}
        new_instructions = []
        for instr in self.instructions:
            if instr[0] == 'LABEL':
                copies.clear()
                new_instructions.append(instr)
            elif instr[0] == 'ASSIGN':
                val, result = instr[1], instr[2]
                if val in copies:
                    val = copies[val]
                
                if isinstance(val, str) and not self.is_number(val) and not val.startswith('"'):
                    copies[result] = val
                else:
                    if result in copies:
                        del copies[result]
                new_instructions.append(('ASSIGN', val, result))
            else:
                new_instr = list(instr)
                for i in range(1, len(new_instr)):
                    if new_instr[i] in copies:
                        new_instr[i] = copies[new_instr[i]]
                new_instructions.append(tuple(new_instr))
        self.instructions = new_instructions

    def dead_code_elimination(self):
        """ Removes assignments to temporaries that are never used. """
        # Find all used variables and temporaries
        used = set()
        for instr in self.instructions:
            if instr[0] in ('ASSIGN', 'PRINT', 'IF_FALSE_GOTO', 'GOTO', 'LABEL'):
                if instr[0] == 'ASSIGN':
                    used.add(instr[1])
                elif instr[0] == 'PRINT':
                    used.add(instr[1])
                elif instr[0] == 'IF_FALSE_GOTO':
                    used.add(instr[1])
            elif len(instr) == 4:
                used.add(instr[1])
                used.add(instr[2])

        new_instructions = []
        for instr in self.instructions:
            if instr[0] == 'ASSIGN':
                val, result = instr[1], instr[2]
                # If result is a temporary and is never used, eliminate it
                if result.startswith('t') and result not in used:
                    continue
            new_instructions.append(instr)
        self.instructions = new_instructions
