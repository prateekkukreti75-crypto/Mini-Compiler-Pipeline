import io
import sys
from contextlib import redirect_stdout
from flask import Flask, request, jsonify
from flask_cors import CORS
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer
from compiler.ir_gen import IRGenerator
from compiler.optimizer import Optimizer
from compiler.cfg import CFG
from compiler.register_allocator import RegisterAllocator
from compiler.vm import VirtualMachine
from compiler.transpiler import CTranspiler

app = Flask(__name__)
CORS(app)

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
        elif len(instr) == 3 and instr[0] in ('!', '-'):
            formatted.append(f"  {instr[2]} = {instr[0]}{instr[1]}")
        else:
            formatted.append(f"  {instr}")
    return '\n'.join(formatted)

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.json
    code = data.get('code', '')
    
    stages = {}
    
    try:
        # 1. Lexical Analysis
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        stages['tokens'] = '\n'.join([str(t) for t in tokens])
        
        # 2. Syntax Analysis
        parser = Parser(tokens, lexer_instance=lexer)
        ast = parser.parse()
        stages['ast'] = str(ast)
        
        # 3. Semantic Analysis
        f = io.StringIO()
        with redirect_stdout(f):
            semantic = SemanticAnalyzer()
            semantic.analyze(ast)
            print("Global Symbol Table:")
            for var, type_ in semantic.symbol_table.scopes[0].items():
                print(f"  {var}: {type_}")
        stages['semantic'] = f.getvalue()
        
        # 4. IR Generation
        ir_gen = IRGenerator()
        ir = ir_gen.generate(ast)
        stages['ir'] = format_ir(ir)
        
        # 5. Code Optimization
        optimizer = Optimizer(ir)
        optimized_ir = optimizer.optimize()
        stages['optimized_ir'] = format_ir(optimized_ir)
        
        # 6. CFG
        f = io.StringIO()
        with redirect_stdout(f):
            cfg = CFG(optimized_ir)
            cfg.build()
            cfg.print_cfg()
        stages['cfg'] = f.getvalue()
        
        # 7. Register Allocation
        f = io.StringIO()
        with redirect_stdout(f):
            allocator = RegisterAllocator(optimized_ir)
            reg_ir, reg_map = allocator.apply_allocation()
            for var, reg in reg_map.items():
                print(f"{var} -> {reg}")
        stages['registers'] = f.getvalue() + "\nIR with Registers:\n" + format_ir(reg_ir)
        
        # 8. VM
        f = io.StringIO()
        with redirect_stdout(f):
            vm = VirtualMachine(optimized_ir)
            vm.run()
        stages['vm'] = f.getvalue()
        
        # 9. Transpiler
        transpiler = CTranspiler(optimized_ir)
        stages['c_code'] = transpiler.transpile()
        
        return jsonify({"success": True, "stages": stages})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "stages": stages})

if __name__ == '__main__':
    app.run(port=5001, debug=True)
