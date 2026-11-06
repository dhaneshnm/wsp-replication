import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2/verify")
from vcommon import *
from collections import Counter

TAB = design_tables()

def probe(args):
    path, seeds = args
    from minatar import Environment
    net = wsp.load_npz(path)
    out = dict(states=0, act_mis=[], xw=[], vw=[], min_a1=1e9, min_a2=1e9, both=0, fmt_x=0, fmt_v=0, comp_bad=0)
    for seed in seeds:
        env = Environment("breakout", sticky_action_prob=0.1); env.seed(seed); env.reset(); e = env.env
        obs = wsp.make_obs_fn(env, "breakout"); rng = np.random.default_rng(seed + 1_000_003)
        for t in range(10_000):
            by, bx, ly, lx, d, pos = e.ball_y, e.ball_x, e.last_y, e.last_x, e.ball_dir, e.pos
            x = obs()
            a1, h1, a2, h2, z = layers(net, x)
            out["states"] += 1
            out["min_a1"] = min(out["min_a1"], float(np.abs(a1[:10]).min()))
            out["min_a2"] = min(out["min_a2"], float(np.abs(a2[:8]).min()))
            netm = move_class(z)
            if z[1] > 0 and z[3] > 0: out["both"] += 1
            Xt = 1 if d in (1, 2) else -1
            Vt = d in (0, 1)
            Xn = 1 if a1[8] > 0 else -1
            Vn = a1[9] > 0
            # my formula for unit 8 / 9 sign (prose): a(bc)-lc>=1 with a(0)=1 ; lr-a'(br)>=1 with a'(8)=7
            aa = 1 if bx == 0 else bx
            if (Xn == 1) != (aa - lx >= 1): out["fmt_x"] += 1
            ap = 7 if by == 8 else by
            if Vn != (ly - ap >= 1): out["fmt_v"] += 1
            # comparator units vs my table at this state (net's own X,V not needed: check every unit)
            for u, nm in enumerate(["D+", "D+", "D-", "D-", "U+", "U+", "U-", "U-"]):
                T = TAB[nm][by, bx]
                want = (T > pos) if u % 2 == 0 else (T < pos)
                if (a1[u] > 0) != want: out["comp_bad"] += 1
            nm = ("U" if Vt else "D") + ("+" if Xt == 1 else "-")
            T = TAB[nm][by, bx]
            orc = 3 if T > pos else (1 if T < pos else 0)
            info = (seed, t, (by, bx), (ly, lx), d, pos, int(e.strike), Xn, int(Vn), netm, orc)
            if netm != orc: out["act_mis"].append(info)
            if Xn != Xt: out["xw"].append(info)
            if Vn != Vt: out["vw"].append(info)
            p = np.exp(z - z.max()); p /= p.sum()
            a = int(rng.choice(6, p=p))
            r, done = env.act(a)
            if done: break
    return out

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    seeds = list(range(1000, 1040))
    with ProcessPoolExecutor(4) as ex:
        parts = list(ex.map(probe, [(CLAUDE, seeds[i::4]) for i in range(4)]))
    tot = dict(states=sum(p["states"] for p in parts), min_a1=min(p["min_a1"] for p in parts),
               min_a2=min(p["min_a2"] for p in parts), both=sum(p["both"] for p in parts),
               fmt_x=sum(p["fmt_x"] for p in parts), fmt_v=sum(p["fmt_v"] for p in parts),
               comp_bad=sum(p["comp_bad"] for p in parts))
    am = sorted(x for p in parts for x in p["act_mis"]); xw = sorted(x for p in parts for x in p["xw"]); vw = sorted(x for p in parts for x in p["vw"])
    print(tot)
    print("action mismatches", len(am), Counter((m[9], m[10]) for m in am))
    for m in am: print("  AM seed,t,ball,trail,dir,pos,strike,Xn,Vn,net,oracle:", m, "inXw", m in xw, "inVw", m in vw)
    print("X wrong", len(xw))
    for m in xw: print("  XW", m)
    print("V wrong", len(vw), "by ball row", Counter(m[2][0] for m in vw), "flat(ball row==trail row)", sum(m[2][0]==m[3][0] for m in vw))
    for m in vw: print("  VW", m)
