import json, pathlib, re, sys, ast
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
logs = pathlib.Path("/Users/dhaneshneelamana/lm_understand-logs")
for g in ["breakout","seaquest","asterix"]:
    r = json.loads((logs/"exp5_write_from_scratch/runs"/g/"reply/run.json").read_text())
    cmd = r.get("cmd", [])
    eff = [c for c in cmd if "effort" in str(c)]
    keys = list(r.keys())
    # find reasoning token counts anywhere
    s = json.dumps(r)
    rt = re.findall(r'"reasoning[_a-z]*tokens?"\s*:\s*(\d+)', s)
    print(g, "effort:", eff, "model:", r.get("model"), "reasoning tokens:", rt)
# parse run_editor argparse defaults via AST (no execution)
src = pathlib.Path("/Users/dhaneshneelamana/projects/wsp-replication/run_editor.py").read_text()
t = ast.parse(src)
for n in ast.walk(t):
    if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "add_argument" and n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value == "--effort":
        print("--effort kwargs:", {k.arg: ast.literal_eval(k.value) for k in n.keywords})
    if isinstance(n, ast.Dict):
        try:
            d = ast.literal_eval(n)
            if "effort" in str(d): print("dict literal:", d)
        except Exception: pass
print("extra_body line:", [l.strip() for l in src.splitlines() if "output_config" in l])
