"""Do the paper's 3 replies ever rely on the reshape branch? Would stricter rules still give hand.npz exactly?"""
import ast
import re
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

EXP = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch"
START = re.compile(r"^\s*(W1|b1|W2|b2|W3|b3)\s*\[")
DEC = re.compile(r"[+-]?(\d+\.?\d*|\.\d+)")


def blocks(text):
    # last block opened by a line '```edits'; it ends at a line that is only ``` (or at the end of the reply)
    m = list(re.finditer(r"^[ \t]*```edits[ \t]*$", text, re.M))
    if not m:
        return None, False
    rest = text[m[-1].end() + 1:]
    end = re.search(r"^[ \t]*```[ \t]*$", rest, re.M)
    return (rest[:end.start()] if end else rest), end is None


def stmts(block):
    out, buf = [], ""
    for raw in block.splitlines():
        line = wsp._strip_comment(raw).rstrip()
        if buf and START.match(line):  # a new statement always starts a new statement
            out.append(buf.strip()); buf = ""
        if not line.strip() and not buf:
            continue
        buf = f"{buf} {line}" if buf else line
        if buf.count("[") - buf.count("]") <= 0:
            out.append(buf.strip()); buf = ""
    if buf.strip():
        out.append(buf.strip())
    return out


def strict_apply(text):
    net = wsp.zero_net()
    block, cut = blocks(text)
    n_ok = n = reshaped = 0
    for st in stmts(block or ""):
        n += 1
        try:
            m = wsp._STMT.match(st)
            name, idx, op, val = m.groups()
            arr = net[name]
            key = wsp._parse_index(idx, arr.ndim)
            v = ast.literal_eval(val.strip())
            for tok in re.findall(r"[^\s\[\],]+", val):
                if not DEC.fullmatch(tok):
                    raise ValueError(f"not a plain decimal: {tok}")
            value = np.asarray(v, dtype=np.float32)
            if not np.all(np.isfinite(value)) or np.any(np.abs(value) > 1e6):
                raise ValueError("range")
            target = arr[key]
            if value.ndim and value.shape != np.shape(target):
                reshaped += 1
                raise ValueError("shape")
            arr[key] = {"=": value, "*=": target * value, "+=": target + value, "-=": target - value}[op]
            n_ok += 1
        except Exception:
            pass
    return net, n_ok, n, reshaped, cut


for g in ["breakout", "seaquest", "asterix"]:
    text = open(f"{EXP}/runs/{g}/reply/answer.md").read()
    hand = wsp.load_npz(f"{EXP}/networks/{g}/hand.npz")
    net, ok, n, reshaped, cut = strict_apply(text)
    d = max(float(np.abs(net[k] - hand[k]).max()) for k in wsp.SHAPES)
    print(f"{g}: strict reader {ok}/{n} statements, shape-mismatch statements={reshaped}, cut_off={cut}, "
          f"max |strict - hand.npz| = {d}")
