import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle, collections, numpy as np
D = os.path.dirname(os.path.abspath(__file__))
NM = ['noop','left','up','right','down','fire']
for nm in ('claude', 'astra'):
    R = pickle.load(open(os.path.join(D, f"rec_{nm}.pkl"), "rb"))
    steps = sum(r['n'] for r in R); pts = sum(r['score'] for r in R)
    causes = collections.Counter(r.get('cause', 'cap') for r in R)
    print(f"== {nm}: episodes {len(R)}, steps {steps}, mean len {steps/len(R):.1f}, mean score {pts/len(R):.3f}, points/step {pts/steps:.4f}")
    print("   end causes:", dict(causes), " collision share %.1f%%" % (100*causes['collision']/len(R)))
    col = [r for r in R if r.get('cause') == 'collision']
    st = [r for r in col if r['steps'][-1]['a'] != r['steps'][-1]['ae']]
    print(f"   collisions {len(col)}: fatal action sticky-changed {len(st)}, policy {len(col)-len(st)}; "
          f"per 100 total steps: policy {100*(len(col)-len(st))/steps:.3f}, sticky {100*len(st)/steps:.3f}")
    nst = sum(1 for r in R for s in r['steps'] if s['a'] != s['ae'])
    print(f"   steps where executed != sampled: {nst} ({100*nst/steps:.2f}%); sticky-collisions per 100 such steps {100*len(st)/nst:.3f}; "
          f"policy collisions per 100 other steps {100*(len(col)-len(st))/(steps-nst):.3f}")
    if nm == 'astra':
        cols = collections.Counter(s['pre']['sx'] for r in R for s in r['steps'])
        ors = collections.Counter(s['pre']['sor'] for r in R for s in r['steps'])
        sa = collections.Counter(s['a'] for r in R for s in r['steps'])
        ea = collections.Counter(s['ae'] for r in R for s in r['steps'])
        print("   astra front col occupancy:", dict(cols), " facing right counts:", dict(ors))
        print("   astra sampled actions:", {NM[k]: v for k, v in sorted(sa.items())})
        print("   astra executed actions:", {NM[k]: v for k, v in sorted(ea.items())})
