import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
NETS = {"claude": wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz"),
        "astra": wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/seaquest/hand.npz")}
AN = ["noop", "left", "up", "right", "down", "fire"]
env = wsp._make_env("seaquest", 0); obsf = wsp.make_obs_fn(env, "seaquest"); E = env.env
def mk(x, y, right=False, oxy=200, d=0, fish=(), subs=(), bul=(), dv=()):
    """objects: (col,row,moving_right)"""
    E.reset(); E.sub_x, E.sub_y, E.sub_or, E.oxygen, E.diver_count = x, y, right, oxy, d
    E.e_fish = [[c, r, lr, 5] for c, r, lr in fish]; E.e_subs = [[c, r, lr, 5, 10] for c, r, lr in subs]
    E.e_bullets = [[c, r, lr] for c, r, lr in bul]; E.divers = [[c, r, lr, 5] for c, r, lr in dv]
    return obsf()
def show(name, x, col=8, expect=""):
    out = []
    for n in (["claude"] if col == 8 else ["astra"]) if False else NETS:
        z = wsp.logits(NETS[n], x); p = np.exp(z - z.max()); p /= p.sum()
        top = np.argsort(-p)[:2]
        out.append(f"{n}: " + ", ".join(f"{AN[i]} {p[i]:.3f}" for i in top))
    print(f"{name:62s} [expect {expect:9s}] " + " | ".join(out))
C = 8  # Claude's column
print("== Claude (sub at col 8 facing left unless stated) ==")
show("start: row0 col5 facing left", mk(5, 0), expect="right")
show("row0 col9 facing right", mk(9, 0, right=True), expect="left")
show("row0 col8 facing left, empty", mk(8, 0), expect="down")
show("row0 col8, enemy row1 col7 moving right", mk(8, 0, fish=[(7, 1, True)]), expect="fire")
show("row0 col8 facing right (back col7)", mk(8, 0, right=True), expect="right")
show("row4 col8 empty, oxy150 d0", mk(8, 4, oxy=150), expect="fire")
show("row4: diver row6 col2 approaching (moving right)", mk(8, 4, oxy=150, dv=[(2, 6, True)]), expect="down")
show("row4: diver row6 col4 receding (moving left)", mk(8, 4, oxy=150, dv=[(4, 6, False)]), expect="fire")
show("row4: diver row2 col2 approaching", mk(8, 4, oxy=150, dv=[(2, 2, True)]), expect="up")
show("row4: diver row5 col9 just spawned moving left", mk(8, 4, oxy=150, dv=[(9, 5, False)]), expect="down")
show("row4: fish row6 col3 receding (moving left)", mk(8, 4, oxy=150, fish=[(3, 6, False)]), expect="down")
show("row4: fish row6 col3 approaching", mk(8, 4, oxy=150, fish=[(3, 6, True)]), expect="down")
show("row4: fish own row col3 approaching", mk(8, 4, oxy=150, fish=[(3, 4, True)]), expect="fire")
show("row4: fish own row col9 moving left (behind)", mk(8, 4, oxy=150, fish=[(9, 4, False)]), expect="up/down")
show("row4: enemy bullet own row col6 moving right", mk(8, 4, oxy=150, bul=[(6, 4, True)]), expect="up/down")
show("row4: enemy bullet own row col5 moving right", mk(8, 4, oxy=150, bul=[(5, 4, True)]), expect="up/down")
show("row4: enemy sub own row col4 moving right", mk(8, 4, oxy=150, subs=[(4, 4, True)]), expect="fire")
show("row4: own-row col9 fish + row3 col7 fish", mk(8, 4, oxy=150, fish=[(9, 4, False), (7, 3, False)]), expect="down")
show("row4: SURF (oxy30 d2)", mk(8, 4, oxy=30, d=2), expect="up")
show("row4: SURF, fish row3 col6 moving left (receding)", mk(8, 4, oxy=30, d=2, fish=[(6, 3, False)]), expect="fire(veto)")
show("row4: SURF, fish row3 col2", mk(8, 4, oxy=30, d=2, fish=[(2, 3, True)]), expect="up")
show("row2: oxy150 d0, nothing", mk(8, 2, oxy=150), expect="fire")
show("row1: oxy150 d0 (no diver)", mk(8, 1, oxy=150), expect="not up")
show("row1: oxy150 d0, danger row1 col9", mk(8, 1, oxy=150, fish=[(9, 1, False)]), expect="down")
show("row1: oxy30 d2 (surface)", mk(8, 1, oxy=30, d=2), expect="up")
show("row1: oxy50 d6 (surface w/ bonus)", mk(8, 1, oxy=50, d=6), expect="up")
show("row1: oxy100 d6 (full, high oxygen)", mk(8, 1, oxy=100, d=6), expect="?")
show("row1: oxy170 d1, danger row1 col9", mk(8, 1, oxy=170, d=1, fish=[(9, 1, False)]), expect="down")
show("row8: fish own row col9", mk(8, 8, oxy=150, fish=[(9, 8, False)]), expect="up")
show("row4: d6 oxy100, diver row6 approaching", mk(8, 4, oxy=100, d=6, dv=[(2, 6, True)]), expect="fire?")
