import sys, re
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
R = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5"
P = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs"
srcs = [("claude", g, f"{R}/{g}/attempt1/answer.md") for g in ("breakout", "asterix")] + \
       [("astra", g, f"{P}/{g}/reply/answer.md") for g in ("breakout", "seaquest", "asterix")]
for who, g, path in srcs:
    text = open(path).read()
    lines = text.splitlines(keepends=True)
    start = next(i for i, l in enumerate(lines) if l.startswith("```edits"))
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("```"))
    body = lines[start + 1:end]
    w3 = [i for i, l in enumerate(body) if re.match(r"\s*(W3|b3)\s*\[", l)]
    first_out = w3[0] if w3 else None
    # simulate a cut after k body lines: read unterminated block, check if output layer is still all zero
    n_live = 0
    for k in range(len(body) + 1):
        cut = "".join(lines[:start + 1] + body[:k])
        net, rep = wsp.apply_edits(cut + "```\n")  # what a cut-off-aware reader would read
        if np.any(net["W3"] != 0) or np.any(net["b3"] != 0):
            n_live += 1
    print(f"{who:6s} {g:8s} block_lines={len(body)} first_W3/b3_line={first_out} "
          f"cut points with nonzero output layer={n_live}/{len(body)+1} "
          f"tail_chars_after_first_W3/b3={len(''.join(body[first_out:])) if first_out is not None else None}")
