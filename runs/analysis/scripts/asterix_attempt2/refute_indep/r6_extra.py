"""Claim 6 extra probes: is lookahead alone sufficient for Claude (stronger weights)? Is Astra's lookahead value sticky-specific?
Usage: r6_extra.py <name> ; seeds 0..199"""
import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2/refute_indep")
import numpy as np
import r5_variants as R
import wsp

def build(name):
    c, a = wsp.load_npz(R.CL), wsp.load_npz(R.AS)
    return {
        "claude_look_w4": (R.claude_add_lookahead(c, 4.0, 1.0), 0.1),
        "claude_look_w8": (R.claude_add_lookahead(c, 8.0, 2.0), 0.1),
        "astra_nolook_nosticky": (R.astra_drop_lookahead(a)[0], 0.0),
    }[name]

def work(args):
    name, seeds = args
    net, st = build(name)
    return [R.play(net, s, st) for s in seeds]

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    name = sys.argv[1]
    seeds = list(range(200)); ch = [seeds[i::4] for i in range(4)]
    with ProcessPoolExecutor(4) as ex:
        res = [x for part in ex.map(work, [(name, c) for c in ch]) for x in part]
    sc = np.array([x[0] for x in res]); ln = np.array([x[1] for x in res])
    print(f"{name} seeds 0..199: mean {sc.mean():.2f} se {sc.std(ddof=1)/np.sqrt(200):.2f} mean_len {ln.mean():.1f}", flush=True)
