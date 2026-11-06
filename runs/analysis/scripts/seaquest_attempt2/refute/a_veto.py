import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle, collections, numpy as np
D = os.path.dirname(os.path.abspath(__file__))
R = pickle.load(open(os.path.join(D, "rec_claude.pkl"), "rb"))
c = collections.Counter()
for r in R:
    for s in r['steps']:
        if not (2 <= s['pre']['sy'] <= 8): continue
        uv = bool(s['h2'][3]); real = s['ch1_rowabove_2to7']; S = s['S'] > 0
        # independent ground truth from game state as well: any fish/esub/bullet in row above, cols 2..7
        row = s['pre']['sy'] - 1
        real_gs = any(e[1] == row and 2 <= e[0] <= 7 for e in s['pre']['fish'] + s['pre']['esub'] + s['pre']['eb'])
        assert real_gs == real
        c['steps'] += 1
        if uv: c['uv'] += 1; c['uv_false'] += (not real)
        if S: c['S'] += 1
        if S and uv: c['S_uv'] += 1; c['S_uv_false'] += (not real)
        if uv and not real:
            c['false_V_lt_-0.9'] += s['V'] < -0.9
print(dict(c))
print("up-veto false share %.1f%%" % (100*c['uv_false']/c['uv']))
print("S on %d steps; up vetoed %d; falsely %d" % (c['S'], c['S_uv'], c['S_uv_false']))
print("=== oxygen deaths with dc>0: S-on steps in rows 2-8 over the episode's final 80 steps ===")
for r in R:
    if r['cause'] != 'oxygen' or r['steps'][-1]['pre']['dc'] == 0: continue
    q = [s for s in r['steps'][-80:] if 2 <= s['pre']['sy'] <= 8 and s['S'] > 0]
    uv = [s for s in q if s['h2'][3]]
    fl = [s for s in uv if not s['ch1_rowabove_2to7']]
    print(f"seed {r['seed']}: S-on steps {len(q)}, up-vetoed {len(uv)}, of which no danger in row-above cols2-7: {len(fl)}")
