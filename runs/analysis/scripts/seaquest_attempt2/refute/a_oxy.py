import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle, collections, numpy as np
D = os.path.dirname(os.path.abspath(__file__))
NM = ['noop','left','up','right','down','fire']
H2 = ['upDesire','dnVeto','dnDesire','upVeto','fireR','fireL','turnR','turnL','stepR','stepL','dodgeUp','dodgeDn','S','R01','surf1','leave01']
R = pickle.load(open(os.path.join(D, "rec_claude.pkl"), "rb"))
print("=== oxygen deaths ===")
ox = [r for r in R if r['cause'] == 'oxygen']
for r in ox:
    s = r['steps'][-1]; on = [H2[j] for j in range(16) if s['h2'][j]]
    # how many of the last 60 steps had S on and up vetoed
    last = r['steps'][-60:]
    sv = sum(1 for q in last if q['h2'][12] and q['h2'][3])
    rows = [q['pre']['sy'] for q in r['steps'][-8:]]
    print(f"seed {r['seed']:3d} dc={s['pre']['dc']} row={s['pre']['sy']} col={s['pre']['sx']} S={s['S']:+.2f} V={s.get('V', float('nan')):+.3f} on={on} "
          f"| last60: S&upVeto on {sv} | last rows {rows}")
print("dc>0:", sum(r['steps'][-1]['pre']['dc'] > 0 for r in ox), "of", len(ox),
      "; last obs has S on AND upVeto on:", sum(bool(r['steps'][-1]['h2'][12] and r['steps'][-1]['h2'][3]) for r in ox))
print("=== surface without diver ===")
for r in R:
    if r['cause'] != 'surface_no_diver': continue
    tail = [(q['t'], q['pre']['sy'], q['pre']['dc'], NM[q['a']], NM[q['ae']]) for q in r['steps'][-4:]]
    print(f"seed {r['seed']}: (t,row,dc,sampled,executed) {tail}")
