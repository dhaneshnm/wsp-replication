import os, pickle, sys
H = os.path.dirname(os.path.abspath(__file__))
A = ["noop", "left", "up", "right", "down", "fire"]
R = {e["seed"]: e for e in pickle.load(open(os.path.join(H, "roll_claude_200.pkl"), "rb"))}
def row_objs(s):
    y = s["y"]
    f = [(o[0], ">" if o[2] else "<") for o in s["fish"] if o[1] == y]
    b = [(o[0], ">" if o[2] else "<") for o in s["subs"] if o[1] == y]
    d = [(o[0], ">" if o[2] else "<") for o in s["divers"] if o[1] == y]
    return f"fish{f} esub{b} div{d}"
def show(seed, t0=None, t1=None):
    e = R[seed]; st = e["steps"]
    t0 = len(st) - 12 if t0 is None else t0; t1 = len(st) if t1 is None else t1
    print(f"--- seed {seed} len {len(st)} score {e['score']}")
    for s in st[max(0, t0):t1]:
        print(f" t{s['t']:4d} y{s['y']} x{s['x']}{'R' if s['right'] else 'L'} oxy{s['oxy']:3d} dc{s['dc']} chose {A[s['a']]:5s} exec {A[s['ea']]:5s}"
              f" p_r={s['pa'][3]:.2f} TR={s['h2'][2]:+.2f} TL={s['h2'][3]:+.2f} CL={s['h2'][4]:+.2f} {row_objs(s)} {'DEAD' if s['done'] else ''}")
show(2, 500, 520)
for sd in (39, 78, 118):
    show(sd, None, None)
    d = R[sd]["death"]
    print("   spawn timer pre-step", d["spawn_timer"], "post enemies at col 9 in sub row:",
          [o for o in d["post_fish"] + d["post_subs"] if o[0] == 9 and o[1] == d["post_y"]], " pre enemies there:",
          [o for o in d["fish"] + d["subs"] if o[0] == 9 and o[1] == d["pre_y"]])
for sd in (6, 21, 31):
    show(sd, None, None)
