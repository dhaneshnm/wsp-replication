import pickle, numpy as np, os
from collections import Counter
A = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3/"
L = lambda f: pickle.load(open(f, "rb"))
def ms(sc): sc = np.asarray(sc, float); return f"mean {sc.mean():.2f} se {sc.std(ddof=1)/np.sqrt(len(sc)):.2f}"
for name in ["claude", "astra"]:
    if not os.path.exists(f"rf_{name}.pkl"): continue
    mine = L(f"rf_{name}.pkl")
    print(f"===== {name}: my runner", ms([r['score'] for r in mine]), "mean steps", np.mean([r['steps'] for r in mine]))
    if os.path.exists(f"rf_{name}_pe.pkl"):
        pe = L(f"rf_{name}_pe.pkl")
        mism = [(m['seed'], (m['score'], m['steps']), p['pe']) for m, p in zip(mine, pe) if (m['score'], m['steps']) != tuple(p['pe'])]
        print("  my runner vs wsp.play_episode, seeds 0-199: mismatches", len(mism), mism[:5])
        an = L(A + f"{name}_200.pkl")
        mism2 = [(a['seed'], (a['score'], a['steps']), p['pe']) for a, p in zip(an, pe) if (a['score'], a['steps']) != tuple(p['pe'])]
        print("  analyst trace pkl vs wsp.play_episode, seeds 0-199: mismatches", len(mism2), mism2[:5])
        print("  analyst pkl causes:", dict(Counter(a['cause'] for a in an)))
    print("  my causes:", dict(Counter(r['cause'] for r in mine)))
    ox = [r for r in mine if r['cause'] == 'oxygen']
    print("  oxygen deaths", len(ox), "share", len(ox) / len(mine), "with d>=1:", sum(r['d_end'] >= 1 for r in ox), "d dist", dict(Counter(r['d_end'] for r in ox)))
    st = np.array([r['steps'] for r in mine]); k = np.array([r['kills'] for r in mine])
    print(f"  kills per 100 steps {100 * k.sum() / st.sum():.3f}  mean steps {st.mean():.1f}  kills/ep {k.mean():.2f}")
    # sticky events
    ev = [e for r in mine for e in r['ev']]
    moved = [e for e in ev if e['moved']]
    fatal = [e for e in moved if e['done']]
    print(f"  sticky-forced vertical (aa!=a, aa in up/down): {len(ev)}; changed row: {len(moved)}; fatal on that step: {len(fatal)}")
    print(f"    fatal & dest row cols 6-9 danger: {sum(e['d69'] for e in fatal)}; fatal & dest danger cols x0-2..x0+1: {sum(e['dnear'] for e in fatal)}")
    print(f"    row-changing with dest cols 6-9 danger: {sum(e['d69'] for e in moved)}; with dnear: {sum(e['dnear'] for e in moved)}")
    print("    x0 of fatal events:", dict(Counter(e['x0'] for e in fatal)))
    # match fatal events to cause
    fat_seeds = {r['seed']: r for r in mine}
    fc = Counter()
    for r in mine:
        for e in r['ev']:
            if e['moved'] and e['done']: fc[r['cause']] += 1
    print("    cause of episodes whose final step was a fatal sticky row change:", dict(fc))
    deaths = sum(r['cause'] != 'cap' for r in mine)
    print("  total deaths", deaths, "; collision deaths", sum(r['cause'] == 'collision' for r in mine),
          "; final step sticky-overridden (aa!=a) among collision deaths:", sum(r['last_a'] != r['last_aa'] for r in mine if r['cause'] == 'collision'))
for cfg in ["claude_sticky0", "astra_sticky0", "claude_guard2"]:
    if os.path.exists(f"rf_{cfg}.pkl"):
        R = L(f"rf_{cfg}.pkl")
        print(cfg, ms([r['score'] for r in R]), "mean steps", round(np.mean([r['steps'] for r in R])), dict(Counter(r['cause'] for r in R)))
