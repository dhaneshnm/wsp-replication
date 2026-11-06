import json, pathlib, re
L = pathlib.Path("/Users/dhaneshneelamana/lm_understand-logs")
E = L / "exp5_write_from_scratch"
readme = (E / "README.md").read_text()
for pat in ["fresh conversation", "no tools", "Codex tool", "sandbox", "approval", "environment context", "permissions", "wrapper"]:
    hits = [i+1 for i, l in enumerate(readme.splitlines()) if pat.lower() in l.lower()]
    print(f"README lines containing {pat!r}: {hits}")
for g in ["breakout", "seaquest", "asterix"]:
    p = (E / "runs" / g / "reply" / "prompt.txt").read_text()
    for pat in ["sandbox", "approval", "environment context", "permissions", "codex", "system prompt", "You have no tools"]:
        if pat.lower() in p.lower():
            print(f"[{g}] prompt contains {pat!r}")
xs, ys = [], []
for g in ["breakout", "seaquest", "asterix"]:
    n = len((E / "runs" / g / "reply" / "prompt.txt").read_text())
    u = json.loads((E / "runs" / g / "reply" / "run.json").read_text())["audit"]["usage"]
    xs.append(n); ys.append(u["input_tokens"])
    print(g, "chars", n, "input_tokens", u["input_tokens"], "cached", u["cached_input_tokens"])
import statistics
mx, my = statistics.mean(xs), statistics.mean(ys)
b = sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / sum((x-mx)**2 for x in xs)
a = my - b*mx
print(f"linear fit tokens = {a:.0f} + {b:.4f}*chars  (marginal {1/b:.2f} chars/token)")
