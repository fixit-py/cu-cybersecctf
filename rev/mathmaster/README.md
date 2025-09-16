## Solution
The code computes the value as follows:
124c: mov -0x14(%rbp), %eax
124f: lea 0x5(%rax), %edx ; edx = x + 5
1252: mov %edx, %eax ; eax = x + 5
1254: add %eax, %eax ; eax = 2*(x+5)
1256: add %edx, %eax ; eax = 3*(x+5)
1258: add %eax, %eax ; eax = 6*(x+5)
125a: cltq ; eax extended to 64-bit in rax
125c: mov %rax, -0x10(%rbp)
1260: cmpq $0x2135831a, -0x10(%rbp) ; compare to 0x2135831a

## Calculation
- The program computes y = 6 × (x + 5) and compares it to the constant 0x2135831a.
- To pass the comparison, solve:
  6*(x + 5) = 0x2135831a
- Therefore:
  x+5 = 0x2135831a/6 = 0x588EB2F
  0x588EB2F is decimal 92,859,183
- Finally:
  x = 0x588EB2F-5 = 0x588EB2A
  decimal 92,859,178

## Result
- Decimal input: 92,859,178

## How to get the flag
Enter the value 92859178 (decimal) or 0x588EB2A (hex) to satisfy the cmp at 1260.
