import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp
from concurrent.futures import ProcessPoolExecutor
D = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt1/"
CL = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/net.npz"

if __name__ == "__main__":
    net = wsp.load_npz(CL)
    seeds = list(range(200)); workers = 4
    chunks = [seeds[i::workers] for i in range(workers)]  # same split as wsp.evaluate
    with ProcessPoolExecutor(workers) as ex:
        parts = list(ex.map(wsp._worker, [(net, "breakout", c) for c in chunks]))
    per = {}
    for c, part in zip(chunks, parts):
        for s, (sc, ln) in zip(c, part):
            per[s] = (sc, ln)
    scores = np.array([r[0] for part in parts for r in part]); lens = np.array([r[1] for part in parts for r in part])
    print("harness path (wsp._worker, evaluate's split): mean", scores.mean(), "se", scores.std(ddof=1) / np.sqrt(len(scores)),
          "max", scores.max(), "mean_length", lens.mean())
    ins = np.load(D + "srcread/instr_scores.npy")
    mism = [(int(s), per[int(s)], (float(a), float(b))) for s, a, b in ins.T if per[int(s)] != (a, b)]
    print("per-episode mismatches vs instr pkl:", len(mism), mism[:5])
