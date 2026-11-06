import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
A="/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt2/"
CL = wsp.load_npz(A+"net.npz")
AS = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/seaquest/hand.npz")
ACT = ['noop','left','up','right','down','fire']
H2N = ['upDes','dnVeto','dnDes','upVeto','fireR','fireL','turnR','turnL','recR','recL','dodgeUp','dodgeDn','S','R01','surf1','leave01']

def fwd(net, x):
    h1 = np.tanh(x @ net["W1"] + net["b1"])
    h2 = np.tanh(h1 @ net["W2"] + net["b2"])
    z = h2 @ net["W3"] + net["b3"]
    p = np.exp(z - z.max()); p /= p.sum()
    return h1, h2, z, p

def make_state(sub=(4,5,False), fish=(), subs=(), divers=(), ebul=(), fbul=(), oxygen=200, dc=0):
    """sub=(row,col,facing_right). fish/subs/divers: (row,col,moving_right). ebul: (row,col,right)."""
    env = wsp._make_env("seaquest", 0)
    e = env.env
    e.sub_y, e.sub_x, e.sub_or = sub
    e.e_fish = [[c, r, d, 5] for (r, c, d) in fish]
    e.e_subs = [[c, r, d, 5, 10] for (r, c, d) in subs]
    e.divers = [[c, r, d, 5] for (r, c, d) in divers]
    e.e_bullets = [[c, r, d] for (r, c, d) in ebul]
    e.f_bullets = [[c, r, d] for (r, c, d) in fbul]
    e.oxygen = oxygen; e.diver_count = dc
    obs = wsp.make_obs_fn(env, "seaquest")
    return obs()

def describe_cl(x, label=""):
    h1, h2, z, p = fwd(CL, x)
    g = x.reshape(10,10,6)
    prow = [r for r in range(10) if g[r,:,0].any()]
    s = f"{label}\n  player rows {prow}; "
    if prow and 2 <= prow[0] <= 8:
        k = prow[0]-2
        s += f"V={h1[k]:+.3f} O={h1[7+k]:+.3f} D={h1[14+k]:+.3f} Y={h1[21+k]:+.3f} "
    s += f"S={h1[28]:+.2f} R01={h1[29]:+.2f}\n"
    on = [f"{H2N[j]}" for j in range(16) if h2[j] > 0]
    s += "  h2 on: " + ",".join(on) + "\n"
    s += "  logits " + " ".join(f"{ACT[i]}={z[i]:+.2f}" for i in range(6)) + "\n"
    s += "  probs  " + " ".join(f"{ACT[i]}={p[i]:.2f}" for i in range(6))
    return s
