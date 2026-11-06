"""Claim 8: bootstrap the kills-per-step difference (200 eps) and test the 1000-episode score gap from recorded files."""
import json, pickle, numpy as np
IN = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3/indep/"
d = {n: pickle.load(open(IN + f"{n}_0.1.pkl", "rb")) for n in ("claude", "astra")}
rng = np.random.default_rng(0)
K = {n: np.array([r["kills"] for r in d[n]]) for n in d}; S = {n: np.array([r["steps"] for r in d[n]]) for n in d}
diffs = []
for _ in range(5000):
    i = rng.integers(0, 200, 200); j = rng.integers(0, 200, 200)
    diffs.append(100 * K["claude"][i].sum() / S["claude"][i].sum() - 100 * K["astra"][j].sum() / S["astra"][j].sum())
diffs = np.array(diffs)
print("kills/100 steps claude", round(100 * K['claude'].sum() / S['claude'].sum(), 3), "astra", round(100 * K['astra'].sum() / S['astra'].sum(), 3),
      "diff 95% CI", np.percentile(diffs, [2.5, 97.5]).round(3))
print("mean steps claude", S["claude"].mean(), "astra", S["astra"].mean(), "diff se", round(np.sqrt(S['claude'].var(ddof=1)/200 + S['astra'].var(ddof=1)/200), 1))
c = json.load(open("/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/run.json"))["score"]
a_paper = json.load(open("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/eval/minatar_eval.json"))["seaquest"]["hand"]
a_local = json.load(open("/Users/dhaneshneelamana/projects/wsp-replication/runs/astra_1000_local.json"))["seaquest"]
for lab, a in (("Astra paper eval", a_paper), ("Astra local harness", a_local)):
    g = a["mean"] - c["mean"]; z = g / np.sqrt(a["se"] ** 2 + c["se"] ** 2)
    print(f"{lab}: {a['mean']:.3f} (se {a['se']:.3f}, len {a['mean_length']:.1f}) vs Claude {c['mean']:.3f} (se {c['se']:.3f}, len {c['mean_length']:.1f}): gap {g:.2f}, z {z:.2f}")
