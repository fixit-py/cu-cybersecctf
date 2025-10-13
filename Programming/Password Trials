#!/usr/bin/env python3
"""
Two-phase password challenge.

Phase 1: first 10 requirements must be satisfied for REQUIRED_ACCEPTED_PHASE1 unique passwords.
When Phase 1 completes the player immediately receives the Phase-1 flag.

Phase 2: additional 20 requirements (total 30) must be satisfied for REQUIRED_ACCEPTED_PHASE2 unique passwords.
When Phase 2 completes the player receives the Phase-2 flag.

Run: python3 password_challenge_2phase.py [--debug]

Optional environment variables:
  FLAG         - default flag used for both phases if PHASE1_FLAG / PHASE2_FLAG not set
  PHASE1_FLAG  - optional custom Phase-1 flag
  PHASE2_FLAG  - optional custom Phase-2 flag
"""
import sys, os, time, argparse, hashlib, re, math
from collections import Counter

# -------------- CONFIG --------------
REQUIRED_ACCEPTED_PHASE1 = 1   # how many unique passwords pass phase 1
REQUIRED_ACCEPTED_PHASE2 = 1   # how many unique passwords pass phase 2 (after phase1)

# Generic limits
PH1_MIN_LEN = 12
PH2_MIN_LEN = 16
MAX_LEN = 25

# Phase2 stricter counts
PH2_MIN_DIGITS = 3
PH2_MIN_SYMBOLS = 2
PH2_MIN_UPPER = 2
PH2_MIN_LOWER = 2

# entropy thresholds (approx Shannon)
PH1_MIN_ENTROPY = 40.0
PH2_MIN_ENTROPY = 60.0

# small banned substrings (case-insensitive)
BANNED = {"password","123456","qwerty","letmein","admin","welcome","iloveyou","flag","test","user","pass"}

# keyboard patterns to reject (simple substrings)
KEYBOARD_PATTERNS = ["qwerty","asdf","zxcv","12345","password","passw0rd"]

# throttle
MIN_SECONDS_BETWEEN_ATTEMPTS = 0.05

# ------------------------------------

LOWER_RE = re.compile(r'[a-z]')
UPPER_RE = re.compile(r'[A-Z]')
DIGIT_RE = re.compile(r'\d')
SYMBOL_RE = re.compile(r'[^A-Za-z0-9]')

def load_flag():
    if 'FLAG' in os.environ:
        return os.environ['FLAG']
    try:
        with open('flag.txt','r') as f:
            return f.read().strip()
    except Exception:
        return "FLAG{example_flag_replace_me}"

def print_phase1_rules():
    print("=== Phase 1 Rules — The Basics ===")
    print("Your password must pass all of the following 10 checks to clear Phase 1:\n")
    print("| #  | Rule | What It Means |")
    print("|----|-------|---------------|")
    print(f"| 1  | Minimum length | Your password must be at least {PH1_MIN_LEN} characters long. |")
    print(f"| 2  | Character variety | Use at least **3 different types** of characters — lowercase, uppercase, numbers, or symbols. |")
    print(f"| 3  | No long repeats | You can’t have more than 2 of the same character in a row (like `aaa` or `111`). |")
    print(f"| 4  | No common or banned words | Don’t include words like {', '.join(sorted(BANNED))}. |")
    print(f"| 5  | No simple sequences | Avoid obvious patterns like `abcd`, `1234`, or reversed ones like `4321`. |")
    print(f"| 6  | Not a palindrome | Don’t use something that reads the same backward and forward (like `abcba`). |")
    print(f"| 7  | Password must be complex enough | It needs enough randomness (entropy ≥ {PH1_MIN_ENTROPY:.1f} bits). |")
    print(f"| 8  | No spaces at the start or end | Don’t start or end with spaces. |")
    print(f"| 9  | No spaces inside | Passwords can’t contain spaces anywhere. |")
    print(f"| 10 | Maximum length | Passwords can’t be longer than {MAX_LEN} characters. |")
    print()


def print_phase2_rules():
    print("=== Phase 2 Rules — The Advanced Challenge ===")
    print("Now it gets tougher! Phase 2 keeps all Phase 1 rules and adds 20 more. You must pass all 30 checks.\n")
    print("| #  | Rule | What It Means |")
    print("|----|-------|---------------|")
    print(f"| 11 | Minimum length | Must be at least {PH2_MIN_LEN} characters long. |")
    print(f"| 12 | Digits required | Must include at least {PH2_MIN_DIGITS} numbers. |")
    print(f"| 13 | Symbols required | Must include at least {PH2_MIN_SYMBOLS} special characters (like `@`, `#`, `!`, etc.). |")
    print(f"| 14 | Uppercase required | Must have at least {PH2_MIN_UPPER} capital letters. |")
    print(f"| 15 | Lowercase required | Must have at least {PH2_MIN_LOWER} lowercase letters. |")
    print(f"| 16 | No overused characters | You can’t use the same character more than 3 times total. |")
    print(f"| 17 | No keyboard patterns | Avoid patterns like {', '.join(KEYBOARD_PATTERNS)}. |")
    print(f"| 18 | No year numbers | Don’t include years between 1900–2099 (e.g., `1999`, `2024`). |")
    print(f"| 19 | No long digit runs | You can’t have 4 or more numbers in a row. |")
    print(f"| 20 | No short palindromes | Even small symmetric words (like `aba` or `1221`) are not allowed. |")
    print(f"| 21 | Must be even more random | Entropy (randomness) must be at least {PH2_MIN_ENTROPY:.1f} bits. |")
    print(f"| 22 | No tiny repeats | Don’t repeat short chunks of 2–4 characters three or more times (like `ababab`). |")
    print(f"| 23 | Must include letters | You can’t use only numbers or symbols — include real letters too. |")
    print(f"| 24 | No long sequences | Avoid runs of 5+ increasing or decreasing letters or numbers. |")
    print(f"| 25 | No admin/system words | Avoid common tech words like admin, root, system, guest, user, test, example. |")
    print(f"| 26 | No long symbol chains | Don’t use 4 or more symbols in a row (like `!!!!`). |")
    print(f"| 27 | At least one unique symbol | You must include at least one different kind of symbol character. |")
    print(f"| 28 | Maximum length | Still can’t exceed {MAX_LEN} characters. |")
    print(f"| 29 | Similarity check (reserved) | Currently not used, but future versions may compare to your Phase 1 passwords. |")
    print(f"| 30 | Phase 1 rules still count | You must still meet all 10 Phase 1 rules too! |")
    print()


def shannon_entropy_bits(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    length = len(s)
    ent = 0.0
    for c, cnt in counts.items():
        p = cnt / length
        ent -= p * math.log2(p)
    return ent * length


def contains_banned(pw: str):
    lw = pw.lower()
    for b in BANNED:
        if b in lw:
            return True
    return False

def has_repeated_run(pw: str, max_run=2):
    run = 1
    for i in range(1,len(pw)):
        if pw[i] == pw[i-1]:
            run += 1
            if run > max_run:
                return True
        else:
            run = 1
    return False

def has_sequence(pw: str, min_len=4):
    if len(pw) < min_len:
        return False
    mapped = []
    for ch in pw:
        if ch.isalpha():
            mapped.append(ord(ch.lower()) - ord('a'))
        elif ch.isdigit():
            mapped.append(26 + ord(ch) - ord('0'))
        else:
            mapped.append(None)
    for i in range(len(mapped)-min_len+1):
        seq = mapped[i:i+min_len]
        if any(x is None for x in seq): continue
        asc = all(seq[j+1]-seq[j]==1 for j in range(len(seq)-1))
        desc = all(seq[j+1]-seq[j]==-1 for j in range(len(seq)-1))
        if asc or desc:
            return True
    return False

def is_palindrome(pw: str, min_len=5):
    if len(pw) < min_len: return False
    return pw == pw[::-1]

def contains_keyboard_pattern(pw: str):
    lw = pw.lower()
    for pat in KEYBOARD_PATTERNS:
        if pat in lw:
            return True
    return False

def contains_year(pw: str):
    # any 4-digit substring in 1900..2099
    for i in range(len(pw)-3):
        sub = pw[i:i+4]
        if sub.isdigit():
            y = int(sub)
            if 1900 <= y <= 2099:
                return True
    return False

def long_shared_substring_with_set(pw: str, seen_hashes: set, required_len=5):
    # This implementation does not keep plaintext accepted passwords for privacy,
    # so we don't check against previous contents here. Function kept for extension.
    return False

def global_char_count_exceeds(pw: str, max_count=4):
    counts = Counter(pw)
    return any(c > max_count for c in counts.values())

# ---------- Phase 1 checks (10) ----------
def check_ph1(pw: str, debug=False):
    # return (True, None) if accepted, else (False, reason)
    if len(pw) < PH1_MIN_LEN:
        return False, f"len<{PH1_MIN_LEN}"
    if len(pw) > MAX_LEN:
        return False, f"len>{MAX_LEN}"
    classes = 0
    classes += 1 if LOWER_RE.search(pw) else 0
    classes += 1 if UPPER_RE.search(pw) else 0
    classes += 1 if DIGIT_RE.search(pw) else 0
    classes += 1 if SYMBOL_RE.search(pw) else 0
    if classes < 3:
        return False, "char-classes<3"
    if has_repeated_run(pw, max_run=2):
        return False, "repeat-run>2"
    if contains_banned(pw):
        return False, "banned-substring"
    if has_sequence(pw, min_len=4):
        return False, "sequence>=4"
    if is_palindrome(pw, min_len=5):
        return False, "palindrome"
    ent = shannon_entropy_bits(pw)
    if ent < PH1_MIN_ENTROPY:
        return False, f"entropy<{PH1_MIN_ENTROPY:.1f}"
    if pw.strip() != pw:
        return False, "leading/trailing-space"
    if ' ' in pw:
        return False, "contains-space"
    return True, None

# ---------- Phase 2 additional checks (20 extra; together -> 30) ----------
def check_ph2_extra(pw: str, accepted_phase1_contents:list=None, debug=False):
    # additional checks beyond phase1. accepted_phase1_contents not used in this simple impl,
    # but left for extension (e.g., check similarity to earlier accepted)
    if len(pw) < PH2_MIN_LEN:
        return False, f"len<{PH2_MIN_LEN}"
    if len(pw) > MAX_LEN:
        return False, f"len>{MAX_LEN}"
    # counts
    digits = len(re.findall(r'\d', pw))
    symbols = len(re.findall(r'[^A-Za-z0-9]', pw))
    uppers = len(re.findall(r'[A-Z]', pw))
    lowers = len(re.findall(r'[a-z]', pw))
    if digits < PH2_MIN_DIGITS:
        return False, f"digits<{PH2_MIN_DIGITS}"
    if symbols < PH2_MIN_SYMBOLS:
        return False, f"symbols<{PH2_MIN_SYMBOLS}"
    if uppers < PH2_MIN_UPPER:
        return False, f"upper<{PH2_MIN_UPPER}"
    if lowers < PH2_MIN_LOWER:
        return False, f"lower<{PH2_MIN_LOWER}"
    # no large global repetition
    if global_char_count_exceeds(pw, max_count=3):
        return False, "char-count-exceeds-3"
    # keyboard patterns
    if contains_keyboard_pattern(pw):
        return False, "keyboard-pattern"
    # year-like substrings
    if contains_year(pw):
        return False, "contains-year"
    # reject consecutive digit run >=4
    if re.search(r'\d{4,}', pw):
        return False, "consecutive-digits>=4"
    # smaller palindrome check
    if is_palindrome(pw, min_len=3):
        return False, "short-palindrome"
    # require stronger entropy
    ent = shannon_entropy_bits(pw)
    if ent < PH2_MIN_ENTROPY:
        return False, f"entropy<{PH2_MIN_ENTROPY:.1f}"
    # no trivial ascii repeated pattern like 'ababab'
    # check for substring of length 2..4 repeated >=3 times
    for L in (2,3,4):
        for i in range(len(pw)-L*3+1):
            part = pw[i:i+L]
            if pw.count(part) >= 3:
                return False, "repeated-substring"
    # ensure not almost only digits+symbols (must keep letters too)
    if (digits + symbols) > len(pw) - 2 and (uppers + lowers) < 2:
        return False, "too-few-letters"
    # disallow very long monotone sequences (>=5) - reuse has_sequence
    if has_sequence(pw, min_len=5):
        return False, "sequence>=5"
    # disallow some common substrings again (longer list)
    big_ban = {"admin","root","operator","system","guest","user","test","example"}
    lw = pw.lower()
    for b in big_ban:
        if b in lw:
            return False, f"contains-{b}"
    # limit runs of punctuation > 3
    if re.search(r'[^A-Za-z0-9]{4,}', pw):
        return False, "punctuation-run>=4"
    # ensure at least 1 unique symbol character (we already check count >=2 earlier)
    if len(set(ch for ch in pw if not ch.isalnum())) < 1:
        return False, "symbols-unique<1"
    return True, None
# ---- Ultra Phase 2 Final Challenge ----
RARE_SYMBOLS = set('^~[]{}<>=?/')

def looks_alternating_pattern(pw: str):
    pattern = ''
    for ch in pw:
        if ch.isalpha():
            pattern += 'L'
        elif ch.isdigit():
            pattern += 'D'
        else:
            pattern += 'S'
    for L in range(2, 5):
        seg = pattern[:L]
        if seg * (len(pattern) // L) == pattern[:(len(pattern)//L)*L]:
            return True
    return False

def avg_ascii_diff(pw: str):
    diffs = [abs(ord(pw[i]) - ord(pw[i-1])) for i in range(1, len(pw))]
    return sum(diffs) / len(diffs) if diffs else 0

def mirrored_halves(pw: str):
    if len(pw) % 2 != 0:
        return False
    mid = len(pw)//2
    return pw[:mid] == pw[mid:]

# wrapper to check phase2 full (phase1 + extras)
def check_phase2_full(pw: str, accepted_phase1_contents:list=None, debug=False):
    ok, reason = check_ph1(pw, debug=debug)
    if not ok:
        return False, f"phase1-failed:{reason}"
    ok2, reason2 = check_ph2_extra(pw, accepted_phase1_contents=accepted_phase1_contents, debug=debug)
    if not ok2:
        return False, f"phase2-extra-failed:{reason2}"
    return True, None
def check_phase2_ultra(pw: str):
    # Option 1–5 merged
    if looks_alternating_pattern(pw):
        return False, "alternating-pattern"
    if not any(ch in RARE_SYMBOLS for ch in pw):
        return False, "no-rare-symbol"
    if avg_ascii_diff(pw) < 5:
        return False, "too-patterned"
    if re.search(r'[A-Za-z]{2,}\d{2,}', pw):
        return False, "missing-separator-between-letters-digits"
    if mirrored_halves(pw):
        return False, "mirrored-halves"
    return True, None


# ------------- interactive loop -------------
# ------------- interactive loop -------------
def interactive_loop(debug=False):
    flag = load_flag()
    phase1_flag_env = "CU{Strong_Start_But_This_Is_Only_Phase1}"
    phase2_flag_env = "CU{Ultimate_Password_Master_You_Broke_The_System}"

    accepted_phase1_hashes = set()
    accepted_phase2_hashes = set()
    accepted_phase1_contents = []  # to allow similarity checks later if desired
    last_time = 0.0

    print("Two-phase Password Challenge")
    print(f"Phase 1: supply {REQUIRED_ACCEPTED_PHASE1} distinct password(s) passing the first 10 requirements.")
    print(f"Phase 2: then supply {REQUIRED_ACCEPTED_PHASE2} distinct password(s) passing all 30 requirements.")
    print("Only 'Accepted' or 'Rejected' will be shown in normal mode. Use --debug to see reasons.\n")
    print_phase1_rules()

    in_phase = 1

    try:
        while True:
            prompt = f"(Phase {in_phase}) > "
            try:
                line = input(prompt)
            except EOFError:
                print("\nEOF; exiting.")
                return 0

            now = time.time()
            if now - last_time < MIN_SECONDS_BETWEEN_ATTEMPTS:
                time.sleep(MIN_SECONDS_BETWEEN_ATTEMPTS - (now - last_time))
            last_time = time.time()

            pw = line.rstrip("\n")
            if not pw:
                print("Rejected")
                if debug:
                    print("[debug] empty")
                continue

            # ---------- Phase 1 ----------
            if in_phase == 1:
                ok, reason = check_ph1(pw, debug=debug)
                if not ok:
                    print("Rejected")
                    if debug:
                        print(f"[debug] phase1 fail: {reason}, entropy={shannon_entropy_bits(pw):.2f}")
                    continue

                h = hashlib.sha256(pw.encode()).hexdigest()
                if h in accepted_phase1_hashes:
                    print("Rejected")
                    if debug:
                        print("[debug] duplicate for phase1")
                    continue

                accepted_phase1_hashes.add(h)
                accepted_phase1_contents.append(pw)
                print(f"Accepted ({len(accepted_phase1_hashes)}/{REQUIRED_ACCEPTED_PHASE1})")

                if len(accepted_phase1_hashes) >= REQUIRED_ACCEPTED_PHASE1:
                    phase1_flag = phase1_flag_env if phase1_flag_env is not None else flag
                    print("\n*** Phase 1 complete! Here is your Phase-1 flag. ***")
                    print("Flag (Phase 1):", phase1_flag)
                    in_phase = 2
                    print_phase2_rules()
                    print("\n--- Now Phase 2: supply stronger passwords to get the Phase-2 flag. ---\n")
                continue

            # ---------- Phase 2 ----------
            if in_phase == 2:
                ok, reason = check_phase2_full(
                    pw, accepted_phase1_contents=accepted_phase1_contents, debug=debug
                )
                if not ok:
                    print("Rejected")
                    if debug:
                        print(f"[debug] phase2 fail: {reason}, entropy={shannon_entropy_bits(pw):.2f}")
                    continue

                h = hashlib.sha256(pw.encode()).hexdigest()
                if h in accepted_phase2_hashes:
                    print("Rejected")
                    if debug:
                        print("[debug] duplicate for phase2")
                    continue

                accepted_phase2_hashes.add(h)
                print(f"Accepted ({len(accepted_phase2_hashes)}/{REQUIRED_ACCEPTED_PHASE2})")

                if len(accepted_phase2_hashes) >= REQUIRED_ACCEPTED_PHASE2:
                    print("\n*** Congratulations — Phase 2 complete! ***")
                    print("Flag (Phase 2): FLAG{CU_Phase2_Fake_Flag}")
                    print("\n😏 Just kidding... there’s ONE MORE hidden challenge!")
                    print("Your next password must start with 'CU' and pass the ultra-rules.")
                    in_phase = 3
                continue

            # ---------- Phase 3 (Secret Ultra Round) ----------
            if in_phase == 3:
                if not pw.startswith("CU"):
                    print("Rejected")
                    if debug:
                        print("[debug] must start with 'CU'")
                    continue

                ok, reason = check_phase2_ultra(pw)
                if not ok:
                    print("Rejected")
                    if debug:
                        print(f"[debug] ultra fail: {reason}")
                    continue

                print("Accepted — you beat the final hidden challenge!")
                real_flag = phase2_flag_env if phase2_flag_env is not None else flag
                print(" Real Final Flag:", real_flag)
                return 0

    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--debug', action='store_true', default=True, help="Enable debug mode (default: ON)")
    args = ap.parse_args()
    sys.exit(interactive_loop(debug=args.debug))


if __name__ == '__main__':
    main()
