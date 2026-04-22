import sys
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer
from compiler.ir_gen import IRGenerator
from compiler.optimizer import Optimizer

def format_ir(instructions):
    formatted = []
    for instr in instructions:
        if len(instr) == 2 and instr[0] == 'LABEL':
            formatted.append(f"{instr[1]}:")
        elif len(instr) == 3 and instr[0] == 'ASSIGN':
            formatted.append(f"  {instr[2]} = {instr[1]}")
        elif len(instr) == 2 and instr[0] == 'PRINT':
            formatted.append(f"  print {instr[1]}")
        elif len(instr) == 4 and instr[0] == 'CALL':
            formatted.append(f"  {instr[3]} = call {instr[1]}, {instr[2]} args")
        elif len(instr) == 4:
            formatted.append(f"  {instr[3]} = {instr[1]} {instr[0]} {instr[2]}")
        elif len(instr) == 3 and instr[0] == 'IF_FALSE_GOTO':
            formatted.append(f"  ifFalse {instr[1]} goto {instr[2]}")
        elif len(instr) == 2 and instr[0] == 'GOTO':
            formatted.append(f"  goto {instr[1]}")
        elif len(instr) == 2 and instr[0] == 'PARAM_PUSH':
            formatted.append(f"  param_push {instr[1]}")
        elif len(instr) == 2 and instr[0] == 'PARAM_POP':
            formatted.append(f"  param_pop {instr[1]}")
        elif len(instr) == 2 and instr[0] == 'RETURN':
            formatted.append(f"  return {instr[1]}")
        elif len(instr) == 1 and instr[0] == 'RETURN_VOID':
            formatted.append(f"  return")
        elif len(instr) == 3 and instr[0] in ('!', '-'): # Unary ops
            formatted.append(f"  {instr[2]} = {instr[0]}{instr[1]}")
        else:
            formatted.append(f"  {instr}")
    return '\n'.join(formatted)

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_file>")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, 'r') as f:
        source_code = f.read()

    print("=== SOURCE CODE ===")
    print(source_code)
    print("===================\n")

    try:
        # 1. Lexical Analysis
        print("1. LEXICAL ANALYSIS")
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        for token in tokens:
            print(f"  {token}")
        print()

        # 2. Syntax Analysis
        print("2. SYNTAX ANALYSIS (AST)")
        parser = Parser(tokens)
        ast = parser.parse()
        # A simple print representation
        print(f"  {ast}")
        print()

        # 3. Semantic Analysis
        print("3. SEMANTIC ANALYSIS")
        semantic = SemanticAnalyzer()
        semantic.analyze(ast)
        print("  Semantic check passed. Global Symbol Table:")
        for var, type_ in semantic.symbol_table.scopes[0].items():
            print(f"    {var}: {type_}")
        print()

        # 4. IR Generation
        print("4. INTERMEDIATE REPRESENTATION (IR) GENERATION")
        ir_gen = IRGenerator()
        ir = ir_gen.generate(ast)
        print(format_ir(ir))
        print()

        # 5. Code Optimization
        print("5. CODE OPTIMIZATION")
        optimizer = Optimizer(ir)
        optimized_ir = optimizer.optimize()
        print("Optimized IR (with constant folding, propagation, CSE, DCE):")
        print(format_ir(optimized_ir))
        print()
        
        # 6. Control Flow Graph (CFG)
        print("6. CONTROL FLOW GRAPH (CFG)")
        from compiler.cfg import CFG
        cfg = CFG(optimized_ir)
        cfg.build()
        cfg.print_cfg()
        print()
        
        # 7. Register Allocation
        print("7. REGISTER ALLOCATION")
        from compiler.register_allocator import RegisterAllocator
        allocator = RegisterAllocator(optimized_ir)
        reg_ir, reg_map = allocator.apply_allocation()
        print("Variables mapped to hardware registers:")
        for var, reg in reg_map.items():
            print(f"  {var} -> {reg}")
        print("\nIR with Registers:")
        print(format_ir(reg_ir))
        print()
        
        # 8. Virtual Machine Execution
        print("8. VIRTUAL MACHINE EXECUTION")
        from compiler.vm import VirtualMachine
        # We run the VM on the optimized IR (before registers, because the VM evaluates string names easily.
        # But we could also run it on reg_ir!) We'll run it on the normal optimized IR.
        vm = VirtualMachine(optimized_ir)
        vm.run()
        
        # 9. C-Code Transpiler (Backend)
        print("9. C-CODE TRANSPILER (BACKEND)")
        from compiler.transpiler import CTranspiler
        transpiler = CTranspiler(optimized_ir)
        c_code = transpiler.transpile()
        with open('output.c', 'w') as f:
            f.write(c_code)
        print("  Successfully generated 'output.c'. You can compile it using: gcc output.c -o my_program")
        print()
        
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == '__main__':
    main()
