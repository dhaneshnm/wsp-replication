import sys, copy
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

CLAUDE = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt2/net.npz"
ASTRA = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/asterix/hand.npz"
ACT = ['n', 'l', 'u', 'r', 'd', 'f']


def load(which):
    return wsp.load_npz(CLAUDE if which == "claude" else ASTRA)


def forward(net, x):
    h1 = np.tanh(x @ net["W1"] + net["b1"])
    h2 = np.tanh(h1 @ net["W2"] + net["b2"])
    z = h2 @ net["W3"] + net["b3"]
    p = np.exp(z - z.max()); p /= p.sum()
    return h1, h2, z, p


def obs(player=(5, 5), ents=()):
    """player=(row, col). ents: list of (row, col, moving_right(bool), is_gold(bool))."""
    o = np.zeros((10, 10, 6), np.float32)
    if player is not None:
        o[player[0], player[1], 0] = 1
    for (r, c, lr, g) in ents:
        o[r, c, 2 if g else 1] = 1
        b = c - 1 if lr else c + 1
        if 0 <= b <= 9:
            o[r, b, 4] = 1
    return o.reshape(600)


def env_obs(inner):
    """Observation from inner MinAtar asterix Env, same mapping as wsp.make_obs_fn."""
    s = inner.state()
    ch = inner.channels
    o = np.zeros((10, 10, 6), np.float32)
    o[..., 0] = s[..., ch['player']]
    o[..., 1] = s[..., ch['enemy']]
    o[..., 2] = s[..., ch['gold']]
    o[..., 4] = s[..., ch['trail']]
    return o.reshape(600)


def try_action(inner, a):
    """Deterministically apply action a (no sticky) to a copy of the inner env; return (r, terminal, copy)."""
    e = copy.deepcopy(inner)
    r, t = e.act(a)
    return r, t, e
