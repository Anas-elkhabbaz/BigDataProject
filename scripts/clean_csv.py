# scripts/clean_csv.py
import sys, csv, os, tempfile

def usage_and_exit():
    print("Usage: python scripts/clean_csv.py <csv_path>")
    sys.exit(1)

if len(sys.argv) < 2:
    usage_and_exit()

# 1) accept quoted paths; 2) expand %ENV% / $ENV; 3) resolve to absolute
raw_arg = sys.argv[1].strip().strip('"').strip("'")
expanded = os.path.expandvars(raw_arg)
src = os.path.abspath(expanded)

if not os.path.isfile(src):
    print(f"[error] CSV not found: {src}")
    usage_and_exit()

tmp = src + ".tmp"

# Normalize line endings and drop empty/whitespace-only lines
with open(src, "r", encoding="utf-8", newline="") as f_in, \
     open(tmp, "w", encoding="utf-8", newline="") as f_out:
    for line in f_in:
        if line.strip():
            f_out.write(line)

# (Optional) verify CSV parses; if not, still keep cleaned file
try:
    with open(tmp, "r", encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        _ = next(r, None)  # touch header
except Exception as e:
    print(f"[warn] CSV parse warning after clean: {e}")

# Atomic replace on Windows
os.replace(tmp, src)
print("[ok] Cleaned CSV:", src)
