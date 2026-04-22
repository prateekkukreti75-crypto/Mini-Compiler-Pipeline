# Mini Compiler Pipeline

This project implements a complete custom language compiler pipeline from scratch in Python, demonstrating every crucial stage from lexical analysis up to intermediate code optimization.

## Stages Implemented

1. **Lexical Analysis (`compiler/lexer.py`)**: Converts raw string source code into a stream of tokens, discarding whitespace and comments.
2. **Syntax Analysis (`compiler/parser.py`)**: A recursive descent parser that validates syntax and constructs an Abstract Syntax Tree (AST).
3. **Semantic Analysis (`compiler/semantic.py`)**: Traverses the AST to check for undeclared variables and perform basic type checking (e.g., mixing `int` and `float`).
4. **Intermediate Representation (IR) Generation (`compiler/ir_gen.py`)**: Converts the AST into linear Three-Address Code (TAC), heavily relying on temporary variables (`t1`, `t2`, etc.) and labels (`L1`, `L2`).
5. **Code Optimization (`compiler/optimizer.py`)**: Reduces data redundancy and improves performance by applying:
    - **Constant Folding:** E.g., `2 * 3` becomes `6` at compile time.
    - **Constant Propagation:** Replaces variables with their known constant values.
    - **Copy Propagation:** Replaces uses of a copied variable with the original.
    - **Dead Code Elimination:** Removes assignments to temporary variables that are never used.

## Example Output (`sample.txt`)

Input Program:
```c
int a = 5;
int b = 10;
// Constant expression
int c = a + 2 * 3; 

// Data redundancy
int d = a;
int e = d + b;

if (e > 10) {
    print(c);
} else {
    print(e);
}
```

When compiled through the pipeline, the **Unoptimized IR** looks like this:
```
  a = 5
  b = 10
  t1 = 2 * 3
  t2 = a + t1
  c = t2
  d = a
  t3 = d + b
  e = t3
  t4 = e > 10
  ifFalse t4 goto L3
L1:
  print c
  goto L2
L3:
  print e
L2:
```

After **Optimization**, the IR is drastically reduced:
```
  a = 5
  b = 10
  c = 11
  d = 5
  e = 15
  ifFalse 1 goto L3
L1:
  print 11
  goto L2
L3:
  print 15
L2:
```

## Running the Compiler

Run the `main.py` driver program and pass a source file as an argument:
```bash
python3 main.py sample.txt
```# Mini-Compiler-Pipeline
