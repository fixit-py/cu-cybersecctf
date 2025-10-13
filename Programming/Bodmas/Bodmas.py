#!/usr/bin/env python3
"""
math.py - BODMAS-only timed CTF challenge (hardcoded defaults)

Hardcoded defaults:
  QUESTIONS = 50
  TIME_PER_QUESTION = 5.0
  TERMS = 12
  DEPTH = 3

Expressions only use symbols and parentheses (no math.* calls).
Integer-only arithmetic; safe AST evaluation (uses ast.Constant only).
Generates long chained expressions by default.
Silent per-question timeout (5s).
"""

import ast
import random
import sys
import os
import time

# ---------- Hardcoded defaults (no CLI overrides) ----------
QUESTIONS = 200
TIME_PER_QUESTION = 5.0  # seconds (silent)
TERMS = 12
DEPTH = 2

# Allowed AST operators
ALLOWED_BINOPS = {ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod, ast.Pow}
ALLOWED_UNARYOPS = {ast.UAdd, ast.USub}

# Operators used for generation
OPS = ['+', '-', '*', '//', '%', '**']

# ---------- Safe AST evaluator (integer-only) ----------
class EvalError(Exception):
    pass

def safe_eval(expr: str):
    """Evaluate expression string using a restricted AST (integers only)."""
    node = ast.parse(expr, mode='eval')
    return _eval_node(node.body)

def _eval_node(node):
    if isinstance(node, ast.Constant):
        v = node.value
        if isinstance(v, int):
            return v
        raise EvalError("Only integer literals allowed")
    if isinstance(node, ast.BinOp):
        if type(node.op) not in ALLOWED_BINOPS:
            raise EvalError("Operator not allowed")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        # Safety checks
        if isinstance(node.op, ast.FloorDiv) or isinstance(node.op, ast.Mod):
            if right == 0:
                raise EvalError("Division/modulo by zero")
        if isinstance(node.op, ast.Pow):
            # limit exponent magnitude and base magnitude
            if not (isinstance(right, int) and 0 <= abs(right) <= 6):
                raise EvalError("Exponent too large")
            if not (isinstance(left, int) and abs(left) <= 1000):
                raise EvalError("Base too large for pow")
            return left ** right
        if isinstance(node.op, ast.Add): return left + right
        if isinstance(node.op, ast.Sub): return left - right
        if isinstance(node.op, ast.Mult): return left * right
        if isinstance(node.op, ast.FloorDiv): return left // right
        if isinstance(node.op, ast.Mod): return left % right
    if isinstance(node, ast.UnaryOp):
        if type(node.op) not in ALLOWED_UNARYOPS:
            raise EvalError("Unary operator not allowed")
        val = _eval_node(node.operand)
        if isinstance(node.op, ast.UAdd): return +val
        if isinstance(node.op, ast.USub): return -val
    if isinstance(node, ast.Expr):
        return _eval_node(node.value)
    raise EvalError(f"Unsupported node: {type(node)}")

# ---------- Expression generator (long chains + nesting) ----------
def gen_int():
    return random.randint(-50, 100)

def fmt_num(n: int) -> str:
    return str(int(n))

def maybe_unary(literal: str, p_unary=0.25):
    """Randomly apply unary + / - in front of a literal (can create sequences)."""
    if random.random() < p_unary:
        u = random.choice(['+', '-'])
        if random.random() < 0.2:
            u2 = random.choice(['+', '-'])
            return f"{u}{u2}({literal})"
        return f"{u}({literal})"
    return literal

def gen_operand(depth, max_depth):
    """Generate either a literal (maybe with unary signs) or a parenthesized subexpression."""
    if depth < max_depth and random.random() < 0.35:
        sub = gen_long_expr(terms=random.randint(2, max(2, 4)), depth=depth+1, max_depth=max_depth)
        return f"({sub})"
    return maybe_unary(fmt_num(gen_int()), p_unary=0.35)

def gen_long_expr(terms=8, depth=0, max_depth=2):
    """Generate a chained expression with 'terms' operands."""
    if terms <= 0:
        return fmt_num(gen_int())
    parts = []
    parts.append(gen_operand(depth, max_depth))
    for i in range(1, terms):
        op = random.choice(OPS)
        if op in ('//', '%'):
            right = str(random.randint(1, 12))
            if random.random() < 0.2 and depth < max_depth:
                right = gen_operand(depth+1, max_depth)
            parts.append(op)
            parts.append(f"({right})")
        elif op == '**':
            exp = str(random.randint(0, 4))
            parts.append(op)
            parts.append(f"({exp})")
        else:
            parts.append(op)
            parts.append(gen_operand(depth, max_depth))
    expr = " ".join(parts)
    if random.random() < 0.25 and depth > 0:
        expr = f"({expr})"
    return expr

# ---------- Cross-platform input-with-timeout (silent) ----------
if os.name == 'nt':
    import msvcrt
    def input_with_timeout(prompt: str, timeout: float):
        sys.stdout.write(prompt)
        sys.stdout.flush()
        buf = ''
        start = time.time()
        while True:
            if msvcrt.kbhit():
                ch = msvcrt.getwche()
                if ch in ('\r', '\n'):
                    sys.stdout.write('\n')
                    return buf
                if ch == '\b':
                    buf = buf[:-1]
                    sys.stdout.write('\b \b')
                else:
                    buf += ch
            if (time.time() - start) > timeout:
                sys.stdout.write('\n')
                return None
            time.sleep(0.01)
else:
    import signal
    class _TO(Exception): pass
    def _handler(signum, frame):
        raise _TO()
    def input_with_timeout(prompt: str, timeout: float):
        old = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, _handler)
        try:
            signal.alarm(int(timeout) if timeout == int(timeout) else int(timeout) + 1)
            return input(prompt)
        except _TO:
            return None
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old)

# ---------- Game loop ----------
def load_flag():
    if 'FLAG' in os.environ:
        return os.environ['FLAG']
    try:
        with open('flag.txt', 'r') as f:
            return f.read().strip()
    except Exception:
        return "CU{E_pow_i_pi_plus_1_eq_0}"

def compare_int_answer(user: str, correct: int):
    if user is None:
        return False
    s = user.strip()
    try:
        if s.lower().startswith(('0x','0b','0o')):
            return int(s, 0) == correct
        return int(s) == correct
    except Exception:
        return False

def run():
    random.seed()
    flag = load_flag()
    solved = 0
    print("Welcome to math challenge!")
    print("Solve problems. Good luck.\n")

    for qnum in range(1, QUESTIONS + 1):
        cur_terms = max(2, TERMS + (qnum // 200))
        cur_depth = max(1, DEPTH + (qnum // 300))
        expr = gen_long_expr(terms=cur_terms, depth=0, max_depth=cur_depth)
        try:
            ans = safe_eval(expr)
        except Exception:
            try:
                expr = gen_long_expr(terms=max(2, cur_terms//2), depth=0, max_depth=cur_depth)
                ans = safe_eval(expr)
            except Exception:
                expr = fmt_num(gen_int())
                ans = safe_eval(expr)

        prompt = f"#{qnum:03d}: {expr}\n> "
        user = input_with_timeout(prompt, TIME_PER_QUESTION)
        if user is None:
            print("Time's up! (no answer received)")
            print(f"You solved {solved} question(s).")
            return 1
        if compare_int_answer(user, ans):
            solved += 1
            print("correct")
            continue
        else:
            print("Wrong answer.")
            print(f"Correct answer was: {ans}")
            print(f"You solved {solved} question(s).")
            return 1

    print("\n*** Congratulations! You solved all questions. ***")
    print("Flag:", flag)
    return 0

if __name__ == "__main__":
    sys.exit(run())
