"""Traced replica of wsp.play_episode for seaquest: same RNG calls, plus death cause and event stats."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp, inspect
from collections import Counter

CAUSE = {135: "enemy_sub", 142: "enemy_sub", 161: "enemy_bullet", 167: "enemy_bullet",
         172: "fish", 179: "fish", 195: "oxygen", 202: "surface_no_diver"}

def make_traced(env):
    base = type(env.env)
    class Traced(base):
        @property
        def terminal(self):
            return self.__dict__.get("_term", False)
        @terminal.setter
        def terminal(self, v):
            if v and not self.__dict__.get("_term", False):
                self.__dict__["_cause_line"] = inspect.currentframe().f_back.f_lineno
            self.__dict__["_term"] = v
        def _surface(self):
            pre_d, pre_o = self.diver_count, self.oxygen
            r = base._surface(self)
            self.__dict__.setdefault("_surf_log", []).append((pre_d, pre_o, r))
            return r
    e = env.env
    term = e.__dict__.pop("terminal", False)
    e.__class__ = Traced
    e.__dict__["_term"] = term
    e.__dict__["_surf_log"] = []
    return e

def run(net, seed, hidden=False, keep_frames=False, sticky=None):
    env = wsp._make_env("seaquest", seed)
    if sticky is not None: env.sticky_action_prob = sticky
    e = make_traced(env)
    obs = wsp.make_obs_fn(env, "seaquest")
    rng = np.random.default_rng(seed + 1_000_003)
    score = 0.0; kills = 0; pickups = 0
    rows = Counter(); cols = Counter(); acts = Counter(); exec_acts = Counter()
    sticky_n = 0
    frames = []; hist = []
    info = dict(seed=seed)
    for t in range(wsp.MAX_STEPS):
        x = obs()
        z = wsp.logits(net, x)
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        pre = dict(x=e.sub_x, y=e.sub_y, orr=e.sub_or, d=e.diver_count, o=e.oxygen)
        rows[e.sub_y] += 1; cols[e.sub_x] += 1; acts[a] += 1
        # replicate Environment.act exactly
        aa = a
        sticky = False
        if env.random.rand() < env.sticky_action_prob:
            aa = env.last_action; sticky = (aa != a)
        env.last_action = aa
        exec_acts[aa] += 1
        nsurf = len(e._surf_log)
        r, done = e.act(aa)
        sticky_n += sticky
        bonus = sum(s[2] for s in e._surf_log[nsurf:])
        kills += r - bonus
        if e.diver_count > pre["d"] and e.sub_y > 0: pickups += e.diver_count - pre["d"]
        score += r
        if keep_frames:
            frames.append(x.reshape(10,10,6).copy())
        hist.append((t, a, aa, pre, sticky))
        if len(hist) > 12: hist.pop(0)
        if done:
            info.update(cause=CAUSE.get(e.__dict__.get("_cause_line"), str(e.__dict__.get("_cause_line"))),
                        last_x=x, last_hist=list(hist),
                        post=dict(x=e.sub_x, y=e.sub_y, orr=e.sub_or, d=e.diver_count, o=e.oxygen,
                                  fish=[list(f) for f in e.e_fish], subs=[list(s) for s in e.e_subs],
                                  bullets=[list(b) for b in e.e_bullets], divers=[list(d) for d in e.divers]),
                        ramp=e.ramp_index)
            break
    else:
        info.update(cause="cap", ramp=e.ramp_index)
    info.update(score=score, steps=t + 1, kills=kills, pickups=pickups, surf=list(e._surf_log),
                rows=dict(rows), cols=dict(cols), acts=dict(acts), exec_acts=dict(exec_acts), sticky=sticky_n)
    if keep_frames: info["frames"] = frames
    return info
