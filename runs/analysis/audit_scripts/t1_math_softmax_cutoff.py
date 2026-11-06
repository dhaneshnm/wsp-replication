import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import math
import numpy as np
import wsp

rng = np.random.default_rng(123)

# ---------- 1. network math vs an independent loop implementation (float64), spec layout
net = {k: rng.normal(0, 1.5, s).astype(np.float32) for k, s in wsp.SHAPES.items()}
worst = 0.0
for trial in range(20):
    x = (rng.random(600) < 0.1).astype(np.float32)
    h1 = [math.tanh(sum(float(x[i]) * float(net["W1"][i, j]) for i in range(600)) + float(net["b1"][j])) for j in range(32)]
    h2 = [math.tanh(sum(h1[i] * float(net["W2"][i, j]) for i in range(32)) + float(net["b2"][j])) for j in range(32)]
    z = [sum(h2[i] * float(net["W3"][i, j]) for i in range(32)) + float(net["b3"][j]) for j in range(6)]
    worst = max(worst, float(np.abs(np.array(z) - wsp.logits(net, x).astype(np.float64)).max()))
print("1. max |wsp.logits - loop reference| over 20 random nets/inputs:", worst)

# spec example W1[12, 0] = 2.5 : input 12 = (row 0, col 2, ch 0) -> unit 0
n2 = wsp.zero_net(); n2["W1"][12, 0] = 2.5; n2["W2"][0, 5] = 1.0; n2["W3"][5, 4] = 1.0
x = np.zeros(600, np.float32); x[(0 * 10 + 2) * 6 + 0] = 1
print("   spec example: logit[4] =", float(wsp.logits(n2, x)[4]), "expected tanh(tanh(2.5)) =", math.tanh(math.tanh(2.5)))

# ---------- 2/3. softmax sampling frequencies and cutoff, through play_episode with a fake env
class FakeEnv:
    def __init__(self, done_at=None, reward_every=1):
        self.calls = []; self.done_at = done_at
        class E: channels = {"paddle": 0, "ball": 1, "trail": 2, "brick": 3}
        self.env = E()
    def state(self):
        return np.zeros((10, 10, 4), bool)
    def act(self, a):
        self.calls.append(a)
        done = self.done_at is not None and len(self.calls) >= self.done_at
        return 1.0, done

holder = {}
def fake_make_env(game, seed, done_at=None):
    holder["env"] = FakeEnv(done_at); return holder["env"]

orig = wsp._make_env
wsp._make_env = fake_make_env
z = np.array([0.0, 1.0, 2.0, -1.0, 0.5, 3.0], np.float32)
n3 = wsp.zero_net(); n3["b3"][:] = z
score, steps, _ = wsp.play_episode(n3, "breakout", seed=0)
acts = np.array(holder["env"].calls)
p = np.exp(z - z.max()); p /= p.sum()
counts = np.bincount(acts, minlength=6)
exp_counts = p * len(acts)
chi2 = float(((counts - exp_counts) ** 2 / exp_counts).sum())
print("2. softmax: n =", len(acts), "observed freq", np.round(counts / len(acts), 4), "softmax", np.round(p, 4), "chi2(5 dof) =", round(chi2, 2))
print("3. cutoff (env never ends): returned steps =", steps, "act() calls =", len(acts), "score =", score)

wsp._make_env = lambda g, s: fake_make_env(g, s, done_at=10_000)
score, steps, _ = wsp.play_episode(n3, "breakout", seed=0)
print("   env ends on step 10,000: steps =", steps, "act() calls =", len(holder["env"].calls), "score (reward 1 per step incl. last) =", score)
wsp._make_env = lambda g, s: fake_make_env(g, s, done_at=1)
score, steps, _ = wsp.play_episode(n3, "breakout", seed=0)
print("   env ends on step 1: steps =", steps, "score =", score)
wsp._make_env = orig
