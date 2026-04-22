#include <stdio.h>
#include <stdbool.h>
#include <string.h>

// Global Variables & Temporaries
long long counter = 0;
long long t10 = 0;
long long t9 = 0;
long long d = 0;
long long b = 0;
long long t6 = 0;
long long c = 0;
long long t5 = 0;
long long t1 = 0;
long long t3 = 0;
long long t7 = 0;
long long result = 0;
long long flag = 0;
long long t8 = 0;
long long t11 = 0;
long long a = 0;
long long message = 0;

long long param_stack[1000];
int param_sp = 0;

int main() {
    a = (long long)5;
    b = (long long)10;
    message = (long long)"Starting calculation";
    goto L1;
FUNC_multiply:;
    y = param_stack[--param_sp];
    x = param_stack[--param_sp];
    t1 = x * y;
    // RETURN t1
    // RETURN_VOID
L1:;
    t3 = a + 6;
    c = (long long)t3;
    t5 = a + 6;
    d = (long long)t5;
    param_stack[param_sp++] = (long long)t3;
    param_stack[param_sp++] = (long long)t5;
    // WARNING: CALL multiply requires hardware stack in flat C.
    // Real implementation would translate to actual C functions.
    result = (long long)t6;
    flag = (long long)1;
    counter = (long long)0;
L2:;
    t7 = counter < 5;
    t8 = flag == 1;
    t9 = t7 && t8;
    if (!t9) goto L3;
    printf("%lld\n", (long long)message);
    t10 = counter + 1;
    counter = (long long)t10;
    t11 = t10 == 4;
    if (!t11) goto L5;
L4:;
    flag = (long long)0;
L5:;
    goto L2;
L3:;
    printf("%lld\n", (long long)result);
    return 0;
}