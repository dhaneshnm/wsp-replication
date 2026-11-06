import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
N = nets()
# Claude's stated ascending tables (from answer.md) for comparison
cl = N["claude"]
def table(net, unit, scale):
    W = net["W1"].reshape(10, 10, 6, 32)
    return W[:, :, 3, unit] / scale
print("Claude unit0 (D+) ball table equals fold(c+(9-r)) for r=0..8:",
      all(abs(table(cl,0,1)[r,c] - fold(c+(9-r)))<1e-6 for r in range(9) for c in range(10)))
print("Claude unit1 (D-) ball table equals fold(c-(9-r)) for r=0..8:",
      all(abs(table(cl,1,1)[r,c] - fold(c-(9-r)))<1e-6 for r in range(9) for c in range(10)))
modes = {"D+": (1, 1), "D-": (-1, 1), "A+": (1, -1), "A-": (-1, -1)}
for name, net in N.items():
    print("=====", name)
    for mname, (vx, vy) in modes.items():
        mism = 0; tot = 0; probs = []
        tgt_rows = []
        for r in range(1, 9):
            row = []
            for c in range(10):
                tr = (r - vy, c - vx)
                if not (0 <= tr[0] <= 9 and 0 <= tr[1] <= 9):
                    row.append(" .")
                    continue
                if vy == -1 and r == 8: row.append(" ."); continue  # ascending into row 8 impossible
                # implied target: paddle cols where no-op is argmax
                acts = []
                for p in range(10):
                    h1, h2, z, pr = forward(net, make_obs((r, c), tr, p))
                    acts.append(int(np.argmax(pr)))
                    probs.append(pr.max())
                noop = [p for p in range(10) if acts[p] == 0]
                # consistency: right of target -> left(1), left of target -> right(3)
                row.append(("%2s" % (",".join(map(str, noop)) if noop else "-")))
                if vy == 1:
                    L = fold(c + vx * (9 - r))
                    tot += 1
                    if noop != [L] and not (net is N["astra"]):
                        mism += 1
            tgt_rows.append(f"  r={r}: " + " ".join(f"{s:>4}" for s in row))
        print(f" mode {mname}: implied no-op paddle column(s) per ball cell (trail = diagonal predecessor)")
        print("\n".join(tgt_rows))
        if vy == 1 and name == "claude":
            print(f"  descending cells where Claude's no-op column != exact landing column: {mism}/{tot}")
        print(f"  min max-prob over probes: {min(probs):.4f}")
