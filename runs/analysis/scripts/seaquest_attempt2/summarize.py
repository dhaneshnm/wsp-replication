import sys, os, json, collections
import numpy as np
D = os.path.dirname(os.path.abspath(__file__))
ACT = ['noop','left','up','right','down','fire']
for nm in ("claude", "astra"):
    res = json.load(open(os.path.join(D, f"instr_{nm}_0_200.json")))
    n = len(res)
    sc = np.array([r['score'] for r in res]); L = np.array([r['steps'] for r in res])
    print(f"===== {nm}: {n} episodes =====")
    print(f"score mean {sc.mean():.3f} (se {sc.std(ddof=1)/np.sqrt(n):.3f}) median {np.median(sc)} max {sc.max()}  length mean {L.mean():.1f} median {np.median(L)}")
    print("score dist:", np.percentile(sc,[10,25,50,75,90]).tolist())
    c = collections.Counter(r['death'] for r in res)
    print("death causes:", dict(c))
    kinds = collections.Counter(r['death_info'].get('kind') for r in res if r['death']=='collision')
    print("collision kinds:", dict(kinds))
    moved = collections.Counter(r['death_info'].get('moved') for r in res if r['death']=='collision')
    print("collision: player move on fatal step:", dict(moved))
    mi = sum(1 for r in res if r['death']=='collision' and r['death_info'].get('moved_into'))
    print("collision: moved into a cell already holding the entity:", mi)
    stk = sum(1 for r in res if r['death']=='collision' and r['death_info'].get('sticky'))
    print("collision: fatal action was a sticky repeat:", stk)
    fa = collections.Counter(r['death_info'].get('a_exec') for r in res if r['death']=='collision')
    print("collision: executed action on fatal step:", dict(fa))
    print("pickups/ep mean", np.mean([r['pickups'] for r in res]), " episodes with >=1 pickup:", sum(r['pickups']>0 for r in res))
    print("surfacings/ep mean", np.mean([r['surfacings'] for r in res]), " eps with >=1 surfacing:", sum(r['surfacings']>0 for r in res), " surf with 6:", sum(r['surf6'] for r in res))
    print("max divers held distribution:", dict(collections.Counter(r['max_dc'] for r in res)))
    ox = [r for r in res if r['death']=='oxygen']
    print("oxygen deaths with dc>0 at death:", sum(r['dc_at_death']>0 for r in ox), "of", len(ox))
    kills = sc  # score includes surface bonus
    rows = np.sum([r['rows'] for r in res], axis=0); rows = rows/rows.sum()
    cols = np.sum([r['cols'] for r in res], axis=0); cols = cols/cols.sum()
    print("row occupancy %:", np.round(100*rows,1).tolist())
    print("col occupancy %:", np.round(100*cols,1).tolist())
    acts = np.sum([r['acts'] for r in res], axis=0); print("sampled action %:", {ACT[i]: round(100*acts[i]/acts.sum(),1) for i in range(6)})
    if nm == "claude":
        Oe = sum(r['O_eval'] for r in res); print(f"O unit (rows2-8): wrong-sign {100*sum(r['O_wrong'] for r in res)/Oe:.1f}%  near-zero {100*sum(r['O_zero'] for r in res)/Oe:.1f}% of {Oe} steps")
    print("steps with an enemy in player's row %:", round(100*sum(r['row_steps_with_enemy'] for r in res)/L.sum(),1))
    # death time vs oxygen
    print("death step for collision deaths: median", np.median([r['death_info']['t'] for r in res if r['death']=='collision']))
    print("score by death cause:", {k: round(float(np.mean([r['score'] for r in res if r['death']==k])),2) for k in c})
