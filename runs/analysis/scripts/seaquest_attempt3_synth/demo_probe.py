import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz")
AN = ["noop", "left", "up", "right", "down", "fire"]
env = wsp._make_env("seaquest", 0); obsf = wsp.make_obs_fn(env, "seaquest"); E = env.env
def mk(x, y, right=False, oxy=200, d=0, fish=(), subs=(), bul=(), dv=()):
    E.reset(); E.sub_x, E.sub_y, E.sub_or, E.oxygen, E.diver_count = x, y, right, oxy, d
    E.e_fish = [[c, r, lr, 5] for c, r, lr in fish]; E.e_subs = [[c, r, lr, 5, 10] for c, r, lr in subs]
    E.e_bullets = [[c, r, lr] for c, r, lr in bul]; E.divers = [[c, r, lr, 5] for c, r, lr in dv]
    return obsf()
L1N = [f"S{r}" for r in range(9)] + [f"R{r}" for r in range(1, 9)] + [f"U{r}" for r in range(1, 9)] + ["HD", "SURF", "HR", "HL"] + ["x"]*3
L2N = [f"Up{r}" for r in range(1, 9)] + ["Down0"] + [f"Down{r}" for r in range(1, 8)] + ["relayR", "relayL", "BLOCK"] + ["x"]*13
def show(name, x):
    pre1 = x @ net["W1"] + net["b1"]; h1 = np.tanh(pre1)
    h2 = np.tanh(h1 @ net["W2"] + net["b2"]); z = h2 @ net["W3"] + net["b3"]
    p = np.exp(z - z.max()); p /= p.sum()
    on1 = [L1N[i] for i in range(29) if h1[i] > 0]
    rpre = {L1N[i]: round(float(pre1[i]), 1) for i in range(9, 17) if abs(pre1[i] + 4.5) > 1e-6 and i != 9 or (i == 9 and abs(pre1[i] + 44.5) > 1e-6)}
    on2 = [L2N[i] for i in range(19) if h2[i] > 0]
    top = np.argsort(-p)[:2]
    print(f"{name:55s} L1on={on1} Rpre={rpre} L2on={on2} logits={np.round(z,1).tolist()} -> " + ", ".join(f"{AN[i]} {p[i]:.3f}" for i in top))
print("== homing / dive ==")
show("start row0 col5 facing L", mk(5, 0))
show("row0 col9 facing R", mk(9, 0, right=True))
show("row0 col8 facing L, empty", mk(8, 0))
show("row0 col8 facing L, fish row1 col7", mk(8, 0, fish=[(7, 1, True)]))
print("== resting / attraction (sub row4 col8 facing L, oxy150 d0) ==")
show("empty", mk(8, 4, oxy=150))
show("diver row6 col2 moving R (approaching)", mk(8, 4, oxy=150, dv=[(2, 6, True)]))
show("diver row6 col4 moving L (receding)", mk(8, 4, oxy=150, dv=[(4, 6, False)]))
show("diver row2 col2 moving R (approaching)", mk(8, 4, oxy=150, dv=[(2, 2, True)]))
show("fish row6 col3 moving R (approaching)", mk(8, 4, oxy=150, fish=[(3, 6, True)]))
show("fish own row col3 moving R", mk(8, 4, oxy=150, fish=[(3, 4, True)]))
print("== danger (U_r) ==")
show("fish own row col9 moving L (behind)", mk(8, 4, oxy=150, fish=[(9, 4, False)]))
show("bullet own row col6 moving R", mk(8, 4, oxy=150, bul=[(6, 4, True)]))
show("diver row3 col2 appr + fish row3 col7 (veto up)", mk(8, 4, oxy=150, dv=[(2, 3, True)], fish=[(7, 3, False)]))
show("diver row5 col2 appr + fish row5 col7 (veto down)", mk(8, 4, oxy=150, dv=[(2, 5, True)], fish=[(7, 5, False)]))
print("== surfacing (SURF/HD/BLOCK) ==")
show("row4 oxy30 d2", mk(8, 4, oxy=30, d=2))
show("row4 oxy45 d2 (above 40)", mk(8, 4, oxy=45, d=2))
show("row4 oxy50 d6", mk(8, 4, oxy=50, d=6))
show("row4 oxy30 d0", mk(8, 4, oxy=30, d=0))
show("row4 oxy30 d2, fish row3 col6 moving L", mk(8, 4, oxy=30, d=2, fish=[(6, 3, False)]))
show("row1 oxy150 d0", mk(8, 1, oxy=150))
show("row1 oxy30 d2", mk(8, 1, oxy=30, d=2))
show("row2 oxy30 d2 (Up_2 path)", mk(8, 2, oxy=30, d=2))
print("== one-row-ahead gap: danger two rows away is invisible ==")
show("row4 diver row3 appr, fish row2 col7", mk(8, 4, oxy=150, dv=[(2, 3, True)], fish=[(7, 2, False)]))
