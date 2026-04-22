class VirtualMachine:
    def __init__(self, instructions):
        self.instructions = instructions
        self.labels = {}
        self.variables = {}
        self.call_stack = []
        self.param_stack = []

    def _build_label_map(self):
        for idx, instr in enumerate(self.instructions):
            if instr[0] == 'LABEL':
                self.labels[instr[1]] = idx

    def run(self):
        self._build_label_map()
        pc = 0
        
        print("\n--- Virtual Machine Execution Output ---")
        
        while pc < len(self.instructions):
            instr = self.instructions[pc]
            op = instr[0]
            
            if op == 'LABEL':
                pass
            
            elif op == 'ASSIGN':
                val, target = instr[1], instr[2]
                if isinstance(val, str) and val in self.variables:
                    self.variables[target] = self.variables[val]
                else:
                    self.variables[target] = val
                    
            elif op == 'PRINT':
                val = instr[1]
                if isinstance(val, str) and val in self.variables:
                    print(self.variables[val])
                elif isinstance(val, str) and val.startswith('"'):
                    print(val[1:-1])
                else:
                    print(val)
                    
            elif op in ('+', '-', '*', '/', '<', '>', '<=', '>=', '==', '!=', '&&', '||'):
                left, right, target = instr[1], instr[2], instr[3]
                l_val = self.variables[left] if isinstance(left, str) and left in self.variables else left
                r_val = self.variables[right] if isinstance(right, str) and right in self.variables else right
                
                if op == '+': res = l_val + r_val
                elif op == '-': res = l_val - r_val
                elif op == '*': res = l_val * r_val
                elif op == '/': res = l_val / r_val
                elif op == '<': res = 1 if l_val < r_val else 0
                elif op == '>': res = 1 if l_val > r_val else 0
                elif op == '<=': res = 1 if l_val <= r_val else 0
                elif op == '>=': res = 1 if l_val >= r_val else 0
                elif op == '==': res = 1 if l_val == r_val else 0
                elif op == '!=': res = 1 if l_val != r_val else 0
                elif op == '&&': res = 1 if (l_val and r_val) else 0
                elif op == '||': res = 1 if (l_val or r_val) else 0
                
                self.variables[target] = res

            elif op == '!':
                val, target = instr[1], instr[2]
                v_val = self.variables[val] if isinstance(val, str) and val in self.variables else val
                self.variables[target] = 1 if not v_val else 0

            elif op == 'IF_FALSE_GOTO':
                cond, label = instr[1], instr[2]
                c_val = self.variables[cond] if isinstance(cond, str) and cond in self.variables else cond
                if not c_val:
                    pc = self.labels[label]
                    continue
                    
            elif op == 'GOTO':
                label = instr[1]
                pc = self.labels[label]
                continue
                
            elif op == 'PARAM_PUSH':
                val = instr[1]
                v_val = self.variables[val] if isinstance(val, str) and val in self.variables else val
                self.param_stack.append(v_val)
                
            elif op == 'PARAM_POP':
                var_name = instr[1]
                self.variables[var_name] = self.param_stack.pop()
                
            elif op == 'CALL':
                func_name, _, target = instr[1], instr[2], instr[3]
                self.call_stack.append((pc + 1, target)) # return address and target variable
                pc = self.labels[f"FUNC_{func_name}"]
                continue
                
            elif op == 'RETURN':
                val = instr[1]
                v_val = self.variables[val] if isinstance(val, str) and val in self.variables else val
                ret_addr, target = self.call_stack.pop()
                if target:
                    self.variables[target] = v_val
                pc = ret_addr
                continue
                
            elif op == 'RETURN_VOID':
                if self.call_stack:
                    ret_addr, _ = self.call_stack.pop()
                    pc = ret_addr
                    continue
                else:
                    break # main return
                    
            pc += 1
            
        print("----------------------------------------\n")
