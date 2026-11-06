import sys, time
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2/verify")
from vcommon import *
PATHS = {"claude": CLAUDE, "astra": ASTRA, "v678": "my_v678.npz", "v8": "my_v8.npz", "vrow1": "my_vrow1.npz", "an678": "../cf2_rows678.npz"}
if __name__ == "__main__":
    name, s0, n, sticky, keep = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), sys.argv[5] == "keep"
    net = wsp.load_npz(PATHS[name])
    t = time.time()
    res = run_many(net, range(s0, s0 + n), sticky=sticky, keep=keep, workers=4)
    sc = np.array([r[1] for r in res]); ln = np.array([r[2] for r in res])
    print(f"{name} seeds {s0}-{s0+n-1} sticky {sticky}: mean {sc.mean():.2f} se {sc.std(ddof=1)/np.sqrt(n):.2f} "
          f"min {sc.min():.0f} max {sc.max():.0f} mean len {ln.mean():.1f} capped {(ln==10000).sum()} distinct scores {sorted(set(sc.tolist()))[:10]} [{time.time()-t:.0f}s]")
    if keep:
        rec = np.concatenate([r[3] for r in res]); ep = np.concatenate([np.full(len(r[3]), r[0]) for r in res])
        np.savez_compressed(f"rec_{name}_{s0}_{sticky}.npz", rec=rec, ep=ep, seeds=np.array([r[0] for r in res]), scores=sc, lens=ln)
