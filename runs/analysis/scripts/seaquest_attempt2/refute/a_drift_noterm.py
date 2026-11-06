import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle, collections, numpy as np
D = os.path.dirname(os.path.abspath(__file__))
H2 = ['upDesire','dnVeto','dnDesire','upVeto','fireR','fireL','turnR','turnL','stepR','stepL','dodgeUp','dodgeDn','S','R01','surf1','leave01']
R = pickle.load(open(os.path.join(D, "rec_claude.pkl"), "rb"))
cat = collections.Counter(); toward = collections.Counter()
for r in R:
    st = r['steps']
    for i, s in enumerate(st):
        pre = s['pre']
        # position after this step: next record's pre, or post for the last step
        nxt = st[i+1]["pre"] if i + 1 < len(st) else None
        if nxt is None: continue
        if not (3 <= pre['sx'] <= 6) or (3 <= nxt['sx'] <= 6) or nxt['sy'] != pre['sy']:
            continue
        row = pre['sy']
        divs = [d for d in pre['div'] if d[1] == row]
        ens = [e for e in pre['fish'] + pre['esub'] if e[1] == row]
        on = {H2[j] for j in range(16) if s['h2'][j]} if 'h2' in s else set()
        if s['a'] != s['ae']: c = 'sticky'
        elif on & {'turnR', 'turnL'}: c = 'turn'
        elif on & {'stepR', 'stepL'}:
            if divs and not ens: c = 'step, diver in row, no enemy'
            elif ens: c = 'step, enemy in row'
            elif any(b[1] == row for b in pre['eb']): c = 'step, bullet in row'
            else: c = 'step, nothing in row'
        else: c = 'other'
        cat[c] += 1
        if c == 'step, diver in row, no enemy':
            dirn = 1 if nxt['sx'] > pre['sx'] else -1
            tw = any((d[0] - pre['sx']) * dirn > 0 for d in divs)
            toward['moved toward a diver' if tw else 'moved away from all divers in row'] += 1
tot = sum(cat.values())
print("exits from front col 3..6 to outside (same row):", tot)
for k, v in cat.most_common(): print(f"  {v:5d} {100*v/tot:5.1f}%  {k}")
print("direction of diver-step exits:", dict(toward))
