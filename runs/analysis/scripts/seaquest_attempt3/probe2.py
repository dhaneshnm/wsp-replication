import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz")
env = wsp._make_env("seaquest", 0); obsf = wsp.make_obs_fn(env, "seaquest"); E = env.env
AN = "nlurdf"
def mk(x, y, right=False, oxy=150, d=0, fish=(), subs=(), bul=(), dv=()):
    E.reset(); E.sub_x, E.sub_y, E.sub_or, E.oxygen, E.diver_count = x, y, right, oxy, d
    E.e_fish = [[c, r, lr, 5] for c, r, lr in fish]; E.e_subs = [[c, r, lr, 5, 10] for c, r, lr in subs]
    E.e_bullets = [[c, r, lr] for c, r, lr in bul]; E.divers = [[c, r, lr, 5] for c, r, lr in dv]
    return obsf()
def act(x): return AN[int(np.argmax(wsp.logits(net, x)))]
def h1(x): return np.tanh(x @ net["W1"] + net["b1"])
print("1) argmax action, sub row r (rows) vs single approaching diver in row q (cols), diver at col 2 moving right:")
print("     q=" + " ".join(str(q) for q in range(1, 9)))
for r in range(1, 9):
    print(f"  r={r} " + " ".join(act(mk(8, r, dv=[(2, q, True)])) for q in range(1, 9)))
print("   same with oxy=30,d=0 irrelevant; with d=2 oxy=150 (HD state matters for row1->0):")
for r in [1, 2]:
    print(f"  r={r} " + " ".join(act(mk(8, r, d=2, dv=[(2, q, True)])) for q in range(1, 9)))
print("\n2) R-unit pre-activation for a single object in row 4 (unit 12), by column; object types/directions:")
W1, b1 = net["W1"], net["b1"]
for lab, kw in [("diver moving right (approaching)", lambda c: dict(dv=[(c, 4, True)])),
                ("diver moving left (receding)", lambda c: dict(dv=[(c, 4, False)])),
                ("fish moving right (approaching)", lambda c: dict(fish=[(c, 4, True)])),
                ("fish moving left (receding)", lambda c: dict(fish=[(c, 4, False)])),
                ("enemy bullet", lambda c: dict(bul=[(c, 4, True)]))]:
    pre = [float((mk(8, 1, **kw(c)) @ W1[:, 12]) + b1[12]) for c in range(10)]
    print(f"  {lab:34s}", " ".join(f"{v:6.1f}" for v in pre))
print("  empty row:", float(mk(8, 1) @ W1[:, 12] + b1[12]))
print("\n3) Gauge units: HD (unit 25) and SURF (unit 26) sign by oxygen (rows) and divers aboard (cols d=0..6)")
print("   oxy  " + "  ".join(f"d={d}" for d in range(7)))
for oxy in [200, 180, 160, 140, 120, 100, 80, 60, 59, 40, 39, 20, 5]:
    cells = []
    for d in range(7):
        h = h1(mk(8, 4, oxy=oxy, d=d)); cells.append(("H" if h[25] > 0 else "-") + ("S" if h[26] > 0 else "-"))
    print(f"   {oxy:3d}  " + "  ".join(f"{c:3s}" for c in cells))
print("\n4) Two approaching divers, one above and one below at equal distance k (sub row 4/5):")
for r in [4, 5]:
    for k in [1, 2, 3]:
        if 1 <= r - k and r + k <= 8:
            print(f"  sub row {r}, divers rows {r-k} and {r+k}: {act(mk(8, r, dv=[(2, r-k, True), (2, r+k, True)]))}")
print("\n5) Veto: sub row 5, attractive diver in row 3 (approaching), danger in row 4 cols:")
for c in range(0, 10):
    print(f"  fish moving left at row4 col{c}: {act(mk(8, 5, dv=[(2, 3, True)], fish=[(c, 4, False)]))}", end=";")
print()
print("\n6) Current-row danger with both neighbours unsafe (sub row 5, fish row5 col9 L, fish rows 4 and 6 col 7 L):",
      act(mk(8, 5, fish=[(9, 5, False), (7, 4, False), (7, 6, False)])))
