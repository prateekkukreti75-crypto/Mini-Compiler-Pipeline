# Mini Compiler Pipeline

This project implements a complete, end-to-end custom language compiler pipeline from scratch in Python. It demonstrates every crucial stage from lexical analysis up to intermediate code optimization, control flow graph construction, register allocation, simulated virtual machine execution, and C-code transpilation.

## Language Features Supported
- **Variable Declarations & Types**: `int`, `float`, `bool` (`true`/`false`), and `string` (`"text"`).
- **Functions**: Function declarations (`func name(int x, int y) int { ... }`), parameters, return statements, and function calls.
- **Control Flow**: `if/else` statements and `while` loops.
- **Logical & Relational Operators**: `&&`, `||`, `!`, `<`, `>`, `<=`, `>=`, `==`, `!=`.
- **Arithmetic**: `+`, `-`, `*`, `/`.

## The 9-Stage Compiler Pipeline

1. **Lexical Analysis (`compiler/lexer.py`)**: Converts raw string source code into a stream of tokens, discarding whitespace and comments. Tracks line and column numbers for precise error reporting.
2. **Syntax Analysis (`compiler/parser.py`)**: A recursive descent parser that validates syntax and constructs an Abstract Syntax Tree (AST). Throws exact contextual arrows pointing to syntax errors.
3. **Semantic Analysis (`compiler/semantic.py`)**: Traverses the AST with a Block-Scoped Symbol Table to check for undeclared variables, missing return statements, and performs type-checking.
4. **Intermediate Representation Generation (`compiler/ir_gen.py`)**: Converts the AST into linear Three-Address Code (TAC), heavily relying on temporary variables (`t1`, `t2`, etc.), labels (`L1`, `L2`), and simulated hardware stack operations (`param_push`/`param_pop`).
5. **Code Optimization (`compiler/optimizer.py`)**: Reduces data redundancy and improves performance by iteratively applying:
    - **Constant Folding:** E.g., `2 * 3` becomes `6` at compile time.
    - **Constant Propagation:** Replaces variables with their known constant values.
    - **Copy Propagation:** Replaces uses of a copied variable with the original.
    - **Common Subexpression Elimination (CSE):** Prevents re-evaluation of math that was already solved earlier.
    - **Dead Code Elimination:** Removes assignments to temporary variables that are never used.
6. **Control Flow Graph (CFG) Construction (`compiler/cfg.py`)**: Organizes the optimized IR into logical Basic Blocks and draws successor/predecessor edges, paving the way for advanced liveness analysis.
7. **Register Allocation (`compiler/register_allocator.py`)**: Maps the infinite number of variables and temporaries down to a simulated finite set of hardware CPU registers (e.g., `R0` through `R7`).
8. **Virtual Machine Execution (`compiler/vm.py`)**: A custom software processor that interprets and runs the Optimized IR line-by-line, complete with a memory map, a function call stack, and real-time execution outputs.
9. **C-Code Transpiler (`compiler/transpiler.py`)**: Translates the custom IR into fully valid, warning-free C code. It automatically infers variable types (`char*` vs `long long`), models the parameter stack, and outputs an `output.c` file that can be natively compiled into an executable.

## Running the Compiler

Run the `main.py` driver program and pass a source file as an argument:
```bash
python3 main.py sample.txt
```

You can then compile the transpiled output into a native macOS executable using:
```bash
gcc output.c -o my_program
./my_program
```

## Example Program (`sample.txt`)

```c
// Global variables
int a = 5;
int b = 10;
string message = "Starting calculation";

// Function definition
func multiply(int x, int y) int {
    return x * y;
}

// Data redundancy (Constant Folding + Propagation + CSE)
int c = a + 2 * 3;
int d = a + 2 * 3; // CSE should catch this!

// Function call
int result = multiply(c, d);

// While loop and Logical Operators
bool flag = true;
int counter = 0;

while (counter < 5 && flag == true) {
    print(message);
    counter = counter + 1;
    if (counter == 4) {
        flag = false; // Escaping the loop early
    }
}

print(result);
```

## Nexus Compiler Web IDE (Frontend & API)

This project also includes a stunning, interactive, glassmorphic React Web Application that visualizes the entire 9-stage pipeline in real-time.

### Starting the Web UI
You need to run both the API backend and the React frontend.

**1. Start the Flask API:**
Open a terminal and run the compiler's backend server (it runs on port `5001`):
```bash
python3 -m pip install flask flask-cors
python3 api.py
```

**2. Start the React Frontend:**
Open a second terminal, navigate into the `frontend` folder, and start the development server:
```bash
cd frontend
npm install
npm start
```

**3. Launch:**
Navigate to `http://localhost:3000` in your web browser. Type your custom language code into the editor, click **Compile**, and click through the tabs on the right to instantly view the Lexer Tokens, AST, IR, Optimizations, CFG, Registers, Virtual Machine Output, and C Code!
