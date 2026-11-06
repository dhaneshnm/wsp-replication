import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle, collections, numpy as np
D = os.path.dirname(os.path.abspath(__file__))
NM = ['noop','left','up','right','down','fire']
H2 = ['upDesire','dnVeto','dnDesire','upVeto','fireR','fireL','turnR','turnL','stepR','stepL','dodgeUp','dodgeDn','S','R01','surf1','leave01']
R = pickle.load(open(os.path.join(D, "rec_claude.pkl"), "rb"))

def Ostate(s, thr=0.5):
    if 'O' not in s: return 'n/a'
    if abs(s['O']) < thr: return 'zero'
    return 'ok' if (s['O'] > 0) == s['pre']['sor'] else 'wrong'

col = [r for r in R if r['cause'] == 'collision']
print("collisions:", len(col))
for thr in (0.5, 0.2, 0.8):
    print(f"O state at fatal obs (|O|<{thr} = zero):", dict(collections.Counter(Ostate(r['steps'][-1], thr) for r in col)))
# all row 2-8 steps
allO = collections.Counter(Ostate(s) for r in R for s in r['steps'] if 'O' in s)
n = sum(allO.values())
print(f"all row2-8 steps {n}: wrong {100*allO['wrong']/n:.1f}%  zero {100*allO['zero']/n:.1f}%  ok {100*allO['ok']/n:.1f}%")

cats = collections.Counter(); ex = collections.defaultdict(list); sub = collections.Counter()
for r in col:
    s = r['steps'][-1]; pre = s['pre']; post = r['post']
    newpos = (post['sx'], post['sy']); oldpos = (pre['sx'], pre['sy'])
    killers = set()
    for kind in ('fish', 'esub', 'eb'):
        for e in pre[kind]:
            if (e[0], e[1]) == newpos: killers.add(kind)
        for e in post[kind]:
            if (e[0], e[1]) == newpos: killers.add(kind)
    # bullet that passed through: bullet at newpos before its move (pre) covered above
    sticky = s['a'] != s['ae']
    mv = 'stay' if newpos == oldpos else ('vert' if newpos[1] != oldpos[1] else 'horiz')
    on = {H2[j] for j in range(16) if s['h2'][j]}
    row = pre['sy']
    div_in_row = any(d[1] == row for d in pre['div'])
    eb_in_row = any(b[1] == row for b in pre['eb'])
    if sticky:
        c = 'sticky'
    elif row <= 1:
        c = 'rows0/1'
    elif mv == 'horiz':
        if on & {'turnR', 'turnL'}: c = 'horiz: turn unit on'
        elif on & {'stepR', 'stepL'}: c = 'horiz: step/recentre unit on, no turn'
        else: c = 'horiz: other'
        sub[(c, Ostate(s))] += 1
    elif mv == 'vert':
        c = 'vertical'
    else:
        if killers == {'eb'} and eb_in_row and div_in_row and s['Y'] < 0:
            c = 'stay: bullet in row, diver in row, Y<0'
        else:
            c = 'stay: other'
    cats[c] += 1; ex[c].append(r['seed'])
for k, v in cats.most_common():
    print(f"{v:4d} {k}  seeds {ex[k][:10]}")
print("horizontal breakdown by O state:", dict(sub))
# with the analyst's two definitions of 'off-centre': front col outside 3..6 at the fatal step's start
fc = collections.Counter('central' if 3 <= r['steps'][-1]['pre']['sx'] <= 6 else 'off' for r in col)
stp = collections.Counter('central' if 3 <= s['pre']['sx'] <= 6 else 'off' for r in R for s in r['steps'])
print("collisions by front col window:", dict(fc), " steps:", dict(stp), " off share of steps %.1f%%" % (100*stp['off']/sum(stp.values())))
print("rate per 100 steps: off %.3f central %.3f" % (100*fc['off']/stp['off'], 100*fc['central']/stp['central']))
# alternative window: both sub cells in 3..6 (the cells where O reads correctly)
def inwin(p):
    back = p['sx'] - 1 if p['sor'] else p['sx'] + 1
    return 3 <= min(p['sx'], back) and max(p['sx'], back) <= 6
fc2 = collections.Counter(inwin(r['steps'][-1]['pre']) for r in col)
st2 = collections.Counter(inwin(s['pre']) for r in R for s in r['steps'])
print("O-correct cells window: collisions", dict(fc2), "steps", dict(st2), "rates in %.3f out %.3f" % (100*fc2[True]/st2[True], 100*fc2[False]/st2[False]))
