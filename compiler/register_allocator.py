class RegisterAllocator:
    def __init__(self, instructions, num_registers=8):
        self.instructions = instructions
        self.num_registers = num_registers
        self.allocation = {}
        
    def allocate(self):
        # 1. Identify all variables and temporaries
        variables = set()
        for instr in self.instructions:
            for item in instr:
                if isinstance(item, str) and not item.startswith('L') and not item.startswith('FUNC_') and not item.startswith('"') and item not in ('LABEL', 'ASSIGN', 'PRINT', 'GOTO', 'IF_FALSE_GOTO', 'PARAM_PUSH', 'PARAM_POP', 'CALL', 'RETURN', 'RETURN_VOID', '+', '-', '*', '/', '<', '>', '<=', '>=', '==', '!=', '&&', '||', '!', 'print', 'call'):
                    variables.add(item)
                    
        # Filter out numbers that were converted to strings
        vars_to_allocate = [v for v in variables if not v.isdigit()]
        
        # 2. Build a naive interference graph (assume all variables interfere for simplicity in mini-compiler, 
        # or do simple linear allocation)
        # We will map each variable to R0, R1, ..., Rn
        # If we run out of registers, we would normally SPILL to memory, but we'll just throw an error or loop.
        
        for i, var in enumerate(vars_to_allocate):
            reg = f"R{i % self.num_registers}"
            self.allocation[var] = reg
            
    def apply_allocation(self):
        self.allocate()
        new_instructions = []
        for instr in self.instructions:
            new_instr = list(instr)
            for i in range(1, len(new_instr)):
                if new_instr[i] in self.allocation:
                    new_instr[i] = self.allocation[new_instr[i]]
            new_instructions.append(tuple(new_instr))
            
        return new_instructions, self.allocation
