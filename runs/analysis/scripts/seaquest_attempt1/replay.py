import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
np.set_printoptions(precision=2, suppress=True)
which, seed, t0, t1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
net = CL if which == "claude" else AS
env = wsp._make_env("seaquest", seed); g = env.env
ob = wsp.make_obs_fn(env, "seaquest")
rng = np.random.default_rng(seed + 1_000_003)
for t in range(t1 + 1):
    x = ob()
    h1, h2, z, p = fwd(net, x)
    a = int(rng.choice(6, p=p))
    if t >= t0:
        r = g.sub_y
        pre = x @ net["W1"] + net["b1"]
        grid = x.reshape(10, 10, 6)
        rowstr = "".join(("S" if grid[r, c, 0] else "") + ("d" if grid[r, c, 1] and not grid[r, c, 2] else "") + ("E" if grid[r, c, 1] and grid[r, c, 2] else "") + ("D" if grid[r, c, 2] and not grid[r, c, 1] else "") + ("t" if grid[r, c, 4] else "") + ("b" if grid[r, c, 3] else "") or "." for c in range(10))
        fish = [(f[0], f[1], "R" if f[2] else "L") for f in g.e_fish if f[1] == r]
        subs = [(f[0], f[1], "R" if f[2] else "L") for f in g.e_subs if f[1] == r]
        if which == "claude":
            info = f"V={h1[r]:+.2f} " + (f"Tpre={pre[9+r-2]:+.2f} E={h1[16+r-2]:+.2f} " if r >= 2 else "") + f"XR={h1[25]:+.2f} XL={h1[26]:+.2f} SURF={h1[24]:+.2f} h2={h2[:6]}"
        else:
            info = f"h2top={np.argsort(-h2[:24])[:3]}"
        print(f"t={t} row={r} front={g.sub_x} face={'R' if g.sub_or else 'L'} oxy={g.oxygen} dc={g.diver_count} rowcells=[{' '.join(rowstr) if False else rowstr}] fish={fish} subs={subs} | {info} | p={p} a={ACT[a]}")
    rr, done = env.act(a)
    if t >= t0 and env.last_action != a: print("   (sticky -> executed", ACT[env.last_action], ")")
    if done: print("DONE at", t); break
