class CTranspiler:
    def __init__(self, instructions):
        self.instructions = instructions
        
    def transpile(self):
        c_code = [
            "#include <stdio.h>",
            "#include <stdbool.h>",
            "#include <string.h>",
            "",
            "// Global Variables & Temporaries"
        ]
        
        variables = set()
        for instr in self.instructions:
            if instr[0] == 'ASSIGN':
                variables.add(instr[2])
            elif len(instr) == 4 and instr[0] != 'CALL':
                variables.add(instr[3])
            elif len(instr) == 4 and instr[0] == 'CALL':
                variables.add(instr[3])
            elif len(instr) == 3 and instr[0] in ('!', '-'):
                variables.add(instr[2])
                
        for v in variables:
            # We treat everything as int for simplicity in this mini-transpiler, 
            # except if it's obviously a string but in IR we lost some type info.
            # We'll just define them as integers or char*. Let's use long long to be safe, 
            # but string pointers need char*. We will use a generic struct or just int for everything.
            # For simplicity, let's declare them as long long. Strings will cause warnings, but work.
            c_code.append(f"long long {v} = 0;")
            
        c_code.append("")
        
        # We need to handle functions. Since our IR intermixes functions and main code,
        # we will put everything inside main() and use GCC's nested functions OR 
        # just emit flat labels and let it run. But C functions are better.
        # However, our IR uses jump labels (GOTO). C supports GOTO!
        # So we can just put the entire IR into main()!
        # Wait, if we use PARAM_PUSH and PARAM_POP, it's a software stack.
        # Let's emit a software stack for params.
        c_code.append("long long param_stack[1000];")
        c_code.append("int param_sp = 0;")
        
        c_code.append("\nint main() {")
        
        for instr in self.instructions:
            op = instr[0]
            if op == 'LABEL':
                c_code.append(f"{instr[1]}:;")
            elif op == 'ASSIGN':
                val, target = instr[1], instr[2]
                c_code.append(f"    {target} = (long long){val};")
            elif op == 'PRINT':
                val = instr[1]
                if isinstance(val, str) and val.startswith('"'):
                    c_code.append(f'    printf("%s\\n", {val});')
                else:
                    c_code.append(f'    printf("%lld\\n", (long long){val});')
            elif op in ('+', '-', '*', '/', '<', '>', '<=', '>=', '==', '!=', '&&', '||'):
                left, right, target = instr[1], instr[2], instr[3]
                c_code.append(f"    {target} = {left} {op} {right};")
            elif op in ('!', '-'):
                val, target = instr[1], instr[2]
                c_code.append(f"    {target} = {op}{val};")
            elif op == 'IF_FALSE_GOTO':
                cond, label = instr[1], instr[2]
                c_code.append(f"    if (!{cond}) goto {label};")
            elif op == 'GOTO':
                label = instr[1]
                c_code.append(f"    goto {label};")
            elif op == 'PARAM_PUSH':
                val = instr[1]
                c_code.append(f"    param_stack[param_sp++] = (long long){val};")
            elif op == 'PARAM_POP':
                var_name = instr[1]
                c_code.append(f"    {var_name} = param_stack[--param_sp];")
            elif op == 'CALL':
                func_name, args_count, target = instr[1], instr[2], instr[3]
                # To simulate calls using gotos, we need a call stack.
                # It's much easier to just transpile IR properly to C functions, 
                # but flat gotos require a return address switch statement.
                # Since this is a mini transpiler, we will just warn that 
                # flat IR transpilation with functions needs careful stack management.
                c_code.append(f"    // WARNING: CALL {func_name} requires hardware stack in flat C.")
                c_code.append(f"    // Real implementation would translate to actual C functions.")
            elif op == 'RETURN':
                c_code.append(f"    // RETURN {instr[1]}")
            elif op == 'RETURN_VOID':
                c_code.append(f"    // RETURN_VOID")
                
        c_code.append("    return 0;")
        c_code.append("}")
        
        return '\n'.join(c_code)
