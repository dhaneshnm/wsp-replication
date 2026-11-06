import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
W1, b1 = CL["W1"], CL["b1"]
print("T unit 11 (row4) ch0 weights:", W1[[I(4,c,0) for c in range(10)], 11])
print("T unit 11 (row4) ch4 weights:", W1[[I(4,c,4) for c in range(10)], 11])
print("T unit 11 (row4) ch1 weights:", W1[[I(4,c,1) for c in range(10)], 11])
print("T unit 11 (row4) ch2 weights:", W1[[I(4,c,2) for c in range(10)], 11])
print("T unit 11 other nonzero rows:", sorted(set(np.nonzero(W1[:,11])[0]//60)), "b1", b1[11])
print("TURN_R W2 col:", CL["W2"][:,2][np.nonzero(CL["W2"][:,2])], "b2", CL["b2"][2], " TURN_L:", CL["W2"][:,3][np.nonzero(CL["W2"][:,3])], CL["b2"][3])
# facing term for an empty row, each sub position
for front in range(10):
    for f in "LR":
        back = front + 1 if f == "L" else front - 1
        if not 0 <= back <= 9: continue
        x = obs(sub=(4, front, f))
        pre = x @ W1 + b1
        cs = tuple(sorted((front, back)))
        print(f"cells {cs} facing {f}: Tpre={pre[11]:+.2f}  (correct sign would be {'+' if f=='L' else '-'})")
def run(seed):
    env = wsp._make_env("seaquest", seed); g = env.env
    ob = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    c = Counter()
    for t in range(wsp.MAX_STEPS):
        x = ob(); z = wsp.logits(CL, x); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        if g.sub_y >= 2:
            back = g.sub_x - 1 if g.sub_or else g.sub_x + 1
            cs = tuple(sorted((g.sub_x, back)))
            xs = np.zeros(600, np.float32); xs[I(g.sub_y, g.sub_x, 0)] = 1; xs[I(g.sub_y, back, 0)] = 1; xs[I(g.sub_y, back, 4)] = 1
            ft = (xs @ W1 + b1)[9 + g.sub_y - 2]
            sgn = "correct" if (ft > 0.2 and not g.sub_or) or (ft < -0.2 and g.sub_or) else ("zero" if abs(ft) < 0.2 else "wrong")
            c[("centre" if cs == (5, 6) else "off", sgn)] += 1
            if cs != (5, 6): c[("offcells", cs, sgn)] += 1
        r, done = env.act(a)
        if done: break
    return c
if __name__ == "__main__":
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(run, range(200), chunksize=10))
    tot = Counter(); [tot.update(r) for r in res]
    for k, v in sorted(tot.items(), key=lambda kv: -kv[1]): print(v, k)
