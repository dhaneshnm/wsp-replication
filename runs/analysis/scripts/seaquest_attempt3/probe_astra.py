import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
net = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/seaquest/hand.npz")
env = wsp._make_env("seaquest", 0); obsf = wsp.make_obs_fn(env, "seaquest"); E = env.env
AN = "nlurdf"
def mk(x, y, right=False, oxy=150, d=0, fish=(), subs=(), bul=(), dv=()):
    E.reset(); E.sub_x, E.sub_y, E.sub_or, E.oxygen, E.diver_count = x, y, right, oxy, d
    E.e_fish = [[c, r, lr, 5] for c, r, lr in fish]; E.e_subs = [[c, r, lr, 5, 10] for c, r, lr in subs]
    E.e_bullets = [[c, r, lr] for c, r, lr in bul]; E.divers = [[c, r, lr, 5] for c, r, lr in dv]
    return obsf()
def P(x):
    z = wsp.logits(net, x); p = np.exp(z - z.max()); return p / p.sum()
def top(x):
    p = P(x); i = np.argsort(-p)[:2]; return " ".join(f"{AN[j]}{p[j]:.2f}" for j in i)
print("Astra, sub col 5 facing left. argmax (prob) vs diver row q (diver at col 2 moving right):")
for r in range(0, 9):
    print(f"  r={r} " + " | ".join(f"q{q}:{top(mk(5, r, dv=[(2, q, True)]))}" for q in range(1, 9)))
print("  empty rows:", " | ".join(f"r{r}:{top(mk(5, r))}" for r in range(9)))
print("diver direction ignored? sub row4, diver row6 col1 moving LEFT (about to exit):", top(mk(5, 4, dv=[(1, 6, False)])))
print("Surface unit 24 (pre-activation sign) by oxygen x divers:")
for oxy in [200, 180, 120, 80, 60, 59, 40, 20]:
    cells = []
    for d in range(7):
        h = np.tanh(mk(5, 4, oxy=oxy, d=d) @ net["W1"] + net["b1"]); cells.append(f"{h[24]:+.2f}")
    print(f"  oxy {oxy:3d}: " + " ".join(cells))
print("own-row danger: fish row4 col7 moving left (behind sub):", top(mk(5, 4, fish=[(7, 4, False)])))
print("own-row danger: fish row4 col6 moving left (behind sub):", top(mk(5, 4, fish=[(6, 4, False)])))
print("own-row: bullet row4 col3 moving right:", top(mk(5, 4, bul=[(3, 4, True)])))
print("own-row: fish row4 col2 moving right (approaching from front):", top(mk(5, 4, fish=[(2, 4, True)])))
print("row above danger: fish row3 col5, oxy30 d2:", top(mk(5, 4, oxy=30, d=2, fish=[(5, 3, False)])))
print("row two above danger, oxy30 d2 (sticky not checked?): fish row2 col5:", top(mk(5, 4, oxy=30, d=2, fish=[(5, 2, False)])))
print("row1, d0 oxy150:", top(mk(5, 1)), "; row1, d2 oxy150:", top(mk(5, 1, d=2)), "; row1 d2 oxy30:", top(mk(5, 1, oxy=30, d=2)))
