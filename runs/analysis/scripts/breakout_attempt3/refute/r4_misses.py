import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import pickle, collections, numpy as np, wsp
BY, BX, LY, LX, D, POS, A, HS, VS, EFF, POSA, DONE, R = range(13)
CLAUDE = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt3/net.npz"
net = wsp.load_npz(CLAUDE)
res = pickle.load(open("play_claude_200.pkl", "rb"))
Rl = [r for e in res for r in e["rallies"]]; M = [r for r in Rl if r["missed"]]
print("misses", len(M))
# --- greedy no-sticky replay of each missed rally from its first frame (Claude ignores bricks: W1 ch2 == 0)
def obs_from(by, bx, ly, lx, pos):
    x = np.zeros(600, np.float32); x[(by*10+bx)*6+3] = 1; x[(ly*10+lx)*6+4] = 1; x[(90+pos)*6] = 1; return x
g_catch = 0
for r in M:
    pos = r["path"][0][POS]
    for f in r["path"]:
        a = int(np.argmax(wsp.logits(net, obs_from(f[BY], f[BX], f[LY], f[LX], pos))))
        if a == 1: pos = max(0, pos-1)
        elif a == 3: pos = min(9, pos+1)
    g_catch += pos in (r["x8"], r["nx8"])
print("greedy no-sticky replay catches", g_catch, "of", len(M))
# --- miss composition
cls = collections.Counter(); slack_by_cls = collections.defaultdict(collections.Counter)
order_detail = collections.Counter()
for r in M:
    ev = r["ev"]
    has_walk = any(e[0] == "walk" for e in ev)
    has_sx = any(e[0] == "exit_sticky" for e in ev)
    # walk followed (strictly later) by a sticky exit in the same direction as the walk
    seq_same = any(w[0] == "walk" and s[0] == "exit_sticky" and s[1] > w[1] and np.sign(s[2]) == np.sign(w[2]) for w in ev for s in ev)
    seq_any = any(w[0] == "walk" and s[0] == "exit_sticky" and s[1] > w[1] for w in ev for s in ev)
    # immediately following frame
    seq_next = any(w[0] == "walk" and s[0] == "exit_sticky" and s[1] == w[1] + 1 and np.sign(s[2]) == np.sign(w[2]) for w in ev for s in ev)
    k = ("walk" if has_walk else "nowalk", "stickyexit" if has_sx else "nostickyexit", "ordered_same_dir" if seq_same else ("ordered_any" if seq_any else "unordered"))
    cls[k] += 1; slack_by_cls[k][r["slack0"]] += 1
    order_detail[("next-frame" if seq_next else "not-next")] += 1 if has_walk else 0
for k, v in cls.items(): print(k, v, "slack0 dist:", dict(sorted(slack_by_cls[k].items())))
print("walk misses whose sticky exit is on the very next frame, same direction:", order_detail)
print("misses by slack0:", dict(sorted(collections.Counter(r["slack0"] for r in M).items())))
# walk-then-sticky-exit in the same rally but is the walk itself sticky? and was the last exit the final one?
w_sticky = sum(1 for r in M for e in r["ev"] if e[0] == "walk" and e[3])
print("walk events in misses that were themselves sticky-driven:", w_sticky, "; total walk events in misses:", sum(1 for r in M for e in r["ev"] if e[0] == "walk"))
# misses with slack0 == 1: what happened
for r in [r for r in M if r["slack0"] == 1][:3]:
    print("slack1 example seed", r["seed"], "x8", r["x8"], "nx8", r["nx8"], "ev", r["ev"])
    for f in r["path"]: print("   ", f)
