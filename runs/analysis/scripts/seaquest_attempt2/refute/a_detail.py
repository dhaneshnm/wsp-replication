import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle, numpy as np
from rlib import CL, layers
D = os.path.dirname(os.path.abspath(__file__))
NM = ['noop','left','up','right','down','fire']
H2 = ['upDesire','dnVeto','dnDesire','upVeto','fireR','fireL','turnR','turnL','stepR','stepL','dodgeUp','dodgeDn','S','R01','surf1','leave01']
R = {r['seed']: r for r in pickle.load(open(os.path.join(D, "rec_claude.pkl"), "rb"))}
def dump(seed, ts):
    r = R[seed]
    for s in r['steps']:
        if s['t'] in ts:
            pre = s['pre']
            print(f"seed {seed} t={s['t']} row={pre['sy']} col={pre['sx']} or={'R' if pre['sor'] else 'L'} dc={pre['dc']} oxy={pre['oxy']} sampled={NM[s['a']]} exec={NM[s['ae']]}"
                  f" V={s.get('V', float('nan')):+.3f} S={s['S']:+.2f} on={[H2[j] for j in range(16) if s['h2'][j]]} p=" + " ".join(f"{NM[i]}:{s['p'][i]:.3f}" for i in range(6)))
            print("     divers", pre['div'], "fish", pre['fish'], "esub", pre['esub'], "eb", pre['eb'])
dump(191, {106, 107, 108, 109})
dump(152, set(range(R[152]['n'] - 4, R[152]['n'])))
dump(145, set(range(R[145]['n'] - 3, R[145]['n'])))
