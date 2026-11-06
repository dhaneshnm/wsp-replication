import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle, collections, numpy as np
D = os.path.dirname(os.path.abspath(__file__))
H2 = ['upDesire','dnVeto','dnDesire','upVeto','fireR','fireL','turnR','turnL','stepR','stepL','dodgeUp','dodgeDn','S','R01','surf1','leave01']
R = pickle.load(open(os.path.join(D, "rec_claude.pkl"), "rb"))
c = collections.Counter(); absD = []
for r in R:
    if r['cause'] != 'collision': continue
    s = r['steps'][-1]; pre = s['pre']; post = r['post']
    if s['a'] != s['ae'] or pre['sy'] <= 1: continue
    if post['sy'] != pre['sy'] or post['sx'] == pre['sx']: continue
    on = {H2[j] for j in range(16) if s['h2'][j]}
    if on & {'turnR', 'turnL'} or not (on & {'stepR', 'stepL'}): continue
    dirn = 1 if post['sx'] > pre['sx'] else -1
    row = pre['sy']
    en_side = [e for e in pre['fish'] + pre['esub'] if e[1] == row and (e[0] - pre['sx']) * dirn > 0]
    div_other = any(d[1] == row and (d[0] - pre['sx']) * dirn < 0 for d in pre['div'])
    eb_other = any(b[1] == row and (b[0] - pre['sx']) * dirn < 0 for b in pre['eb'])
    killer_in_row_enemy = any((e[0], e[1]) == (post['sx'], post['sy']) for e in pre['fish'] + pre['esub'] + post['fish'] + post['esub'])
    killer_bullet = any((b[0], b[1]) == (post['sx'], post['sy']) for b in pre['eb'] + post['eb'])
    c['n'] += 1
    c['enemy in row on the side moved'] += bool(en_side)
    c['killed by fish/sub'] += killer_in_row_enemy
    c['killed by bullet'] += killer_bullet
    c['|D|>=0.716'] += abs(s['D']) >= 0.716
    c['diver on other side'] += div_other
    c['bullet on other side'] += eb_other
    c['D sign == move dir'] += (np.sign(s['D']) == dirn)
    c['front col 0-2/7-9'] += not (3 <= pre['sx'] <= 6)
    absD.append(abs(s['D']))
print(dict(c))
print("|D| quantiles:", np.round(np.quantile(absD, [0, .25, .5, .75, 1]), 3))
# column occupancy of the Claude sub (front col)
occ = collections.Counter(s['pre']['sx'] for r in R for s in r['steps'])
tot = sum(occ.values())
print("front-col occupancy %:", {k: round(100*v/tot, 2) for k, v in sorted(occ.items())})
