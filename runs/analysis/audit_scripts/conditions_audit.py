"""Compare what run_editor.py sends to Claude with what the paper's Codex runs sent to Astra."""
import ast
import json
import pathlib
import sys

sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")

LOGS = pathlib.Path("/Users/dhaneshneelamana/lm_understand-logs")
EXP = LOGS / "exp5_write_from_scratch"
RE = pathlib.Path("/Users/dhaneshneelamana/projects/wsp-replication/run_editor.py")

# 1. prompt bytes: message.txt vs reply/prompt.txt vs what run_editor reads (Path.read_text())
for g in ["breakout", "seaquest", "asterix"]:
    msg = (EXP / "runs" / g / "message.txt").read_bytes()
    pr = (EXP / "runs" / g / "reply" / "prompt.txt").read_bytes()
    re_read = (EXP / "runs" / g / "reply" / "prompt.txt").read_text()  # exactly as run_editor does
    print(f"[{g}] message==prompt: {msg == pr}; run_editor text == bytes: {re_read.encode() == msg}; "
          f"chars {len(re_read)}")

# 2. system text
sys_codex = [(EXP / "runs" / g / "instructions.md").read_bytes() for g in ["breakout", "seaquest", "asterix"]]
sys_re = (LOGS / "harness" / "instructions.md").read_text().strip()
print("per-game instructions.md identical:", len(set(sys_codex)) == 1, repr(sys_codex[0]))
print("run_editor system:", repr(sys_re), "| equal to Codex file bytes:", sys_re.encode() == sys_codex[0],
      "| equal after strip:", sys_re.encode() == sys_codex[0].strip())

# 3. Codex-side input-token overhead (prompt + instructions vs reported input_tokens)
print("\nCodex reported input_tokens vs prompt size:")
for g in ["breakout", "seaquest", "asterix"]:
    r = json.loads((EXP / "runs" / g / "reply" / "run.json").read_text())
    u = r["audit"]["usage"]
    n = len((EXP / "runs" / g / "reply" / "prompt.txt").read_text())
    for cpt in (3.5, 4.0):
        est = n / cpt
        print(f"  [{g}] input_tokens={u['input_tokens']} prompt_chars={n} est_prompt_tokens(@{cpt} ch/tok)={est:.0f} "
              f"-> implied Codex-added tokens ~{u['input_tokens'] - est:.0f}")
    print(f"  [{g}] effort in cmd: {[c for c in r['cmd'] if 'effort' in c]}, model: {r['cmd'][r['cmd'].index('-m') + 1]}, "
          f"output_tokens={u['output_tokens']}, reasoning={u['reasoning_output_tokens']}, attempt={r['attempt']}, "
          f"limit={r['limit']}")

# 4. run_editor defaults and request shape (static, from its AST)
src = RE.read_text()
tree = ast.parse(src)
defaults = {}
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "add_argument":
        name = node.args[0].value
        for kw in node.keywords:
            if kw.arg == "default":
                defaults[name] = ast.literal_eval(kw.value)
print("\nrun_editor defaults:", defaults)
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "stream":
        print("messages.stream kwargs:", [kw.arg for kw in node.keywords])
print("'tools' passed:", "tools=" in src, "| stop_reason checked before scoring:",
      "stop_reason ==" in src or "stop_reason !=" in src or "if usage[\"stop_reason\"]" in src)
