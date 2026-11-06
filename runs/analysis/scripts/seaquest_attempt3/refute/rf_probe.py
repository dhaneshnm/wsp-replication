import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz")
env = wsp._make_env("seaquest", 0); obsf = wsp.make_obs_fn(env, "seaquest"); E = env.env
def mk(x, y, oxy=150, d=0, fish=()):
    E.reset(); E.sub_x, E.sub_y, E.sub_or, E.oxygen, E.diver_count = x, y, False, oxy, d
    E.e_fish = [[c, r, lr, 5] for c, r, lr in fish]; E.e_subs = []; E.e_bullets = []; E.divers = []
    return obsf()
h1 = lambda x: np.tanh(x @ net["W1"] + net["b1"])
# Claim 7: exhaustive gauge check
bad_surf = []; bad_hd_meet = []; hd_vs_reply = []; meet_states = 0
for d in range(-1, 7):
    for oxy in range(0, 201):
        x = mk(8, 4, oxy=oxy, d=d); g = x.reshape(10, 10, 6)[9, :, 5]
        h = h1(x); S = h[26] > 0; H = h[25] > 0
        pred_S = (1 <= d <= 5 and oxy < 40) or (d == 6 and oxy < 60)
        if S != pred_S: bad_surf.append((d, oxy, S))
        meet = d >= 1 and g[0:9].all()
        meet_states += meet
        if meet and H: bad_hd_meet.append((d, oxy))
        reply_H = bool(g[8]) and not g[0:8].all()
        if H != reply_H: hd_vs_reply.append((d, oxy, H))
print("SURF sign != (d1-5 & oxy<40 or d6 & oxy<60) over d=-1..6, oxy=0..200:", len(bad_surf), bad_surf[:10])
print("states where bars meet:", meet_states, " of which HD on:", len(bad_hd_meet), bad_hd_meet[:5])
print("HD sign != reply rule (gauge col8 lit AND some col0-7 dark):", len(hd_vs_reply), hd_vs_reply[:10])
# Claim 10: up logit at rows 1..8 with SURF on (oxy 30, d 2), nothing else on screen
for y in range(1, 9):
    z = wsp.logits(net, mk(8, y, oxy=30, d=2)); print(f"row {y}: up {z[2]:.2f} fire {z[5]:.2f} down {z[4]:.2f} noop {z[0]:.2f} left {z[1]:.2f} right {z[3]:.2f}")
print("W3[0:8,2] =", net["W3"][0:8, 2], " b3 =", net["b3"], " W3[18,2] =", net["W3"][18, 2])
# Claim 11: adjacency of vetoes in W2 (U units 17..24 -> L2 units 0..15)
W2 = net["W2"]
for j in range(16):
    nz = {int(i): float(W2[i, j]) for i in range(17, 25) if W2[i, j] != 0}
    print(("Up_%d" % (j + 1)) if j < 8 else ("Down_%d" % (j - 8)), "U-unit weights (L1 unit: w):", nz)
print("W2[18,8] (Down_0 <- U_2):", W2[18, 8])
