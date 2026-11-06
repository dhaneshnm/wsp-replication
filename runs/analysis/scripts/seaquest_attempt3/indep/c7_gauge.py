"""Claim 7: exhaustive sweep of oxygen 0..200 x divers 0..6 through real env states; HD (unit 25), SURF (unit 26)."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3/indep")
import numpy as np, wsp, myrun
net = wsp.load_npz(myrun.CLAUDE)
for u in (25, 26):
    rows = sorted({i // 60 for i in np.nonzero(net["W1"][:, u])[0]})
    print(f"unit {u}: input rows with nonzero weight {rows}; channels {sorted({i % 6 for i in np.nonzero(net['W1'][:, u])[0]})}")
env = wsp._make_env("seaquest", 0); E = env.env
surf_on = set(); hd = {}
for oxy in range(0, 201):
    for d in range(0, 7):
        E.reset(); E.sub_x, E.sub_y, E.oxygen, E.diver_count = 8, 4, oxy, d
        h1 = np.tanh(myrun.obs_vec(E) @ net["W1"] + net["b1"])
        if h1[26] > 0: surf_on.add((oxy, d))
        hd[(oxy, d)] = h1[25] > 0
expected = {(o, d) for o in range(201) for d in range(7) if (1 <= d <= 5 and o < 40) or (d == 6 and o < 60)}
print("SURF on set == {d=1..5 & oxy<40} U {d=6 & oxy<60}:", surf_on == expected, "| extra", sorted(surf_on - expected)[:5], "missing", sorted(expected - surf_on)[:5])
for d in range(7):
    ons = [o for o in range(201) if (o, d) in surf_on]
    print(f"  d={d}: SURF on for oxygen {min(ons) if ons else None}..{max(ons) if ons else None} ({len(ons)} values)")
meet = {(o, d) for o in range(201) for d in range(7) if (o * 10 // 200) + d >= 9}
print("HD off on every (oxy,d) where bars meet (oxygen cells + diver cells >= 9):", all(not hd[k] for k in meet), "| #meet states", len(meet))
print("HD on for every d>=1 state where bars do not meet:", all(hd[(o, d)] for o in range(201) for d in range(1, 7) if (o, d) not in meet))
print("HD on for any d=0 state:", any(hd[(o, 0)] for o in range(201)))
print("HD at oxygen>=160 for any d:", any(hd[(o, d)] for o in range(160, 201) for d in range(7)))
for d in range(1, 7):
    offs = [o for o in range(201) if not hd[(o, d)]]
    print(f"  d={d}: HD off from oxygen {min(offs)} upward" if offs else f"  d={d}: HD never off")
