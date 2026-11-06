import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from concurrent.futures import ProcessPoolExecutor
from minatar import Environment
def ep(args):
    which, seed, sticky, greedy = args
    net = NET if which=="claude" else AST
    env = Environment("asterix", sticky_action_prob=sticky); env.seed(seed); env.reset()
    ob = wsp.make_obs_fn(env, "asterix"); rng=np.random.default_rng(seed+1_000_003); sc=0
    for t in range(wsp.MAX_STEPS):
        z=wsp.logits(net, ob()); p=np.exp(z-z.max()); p/=p.sum()
        a = int(np.argmax(z)) if greedy else int(rng.choice(6,p=p))
        r,d=env.act(a); sc+=r
        if d: return sc, t+1
    return sc, wsp.MAX_STEPS
if __name__=="__main__":
    for which in ("claude","astra"):
        for sticky, greedy in ((0.0,False),(0.1,True)):
            with ProcessPoolExecutor(4) as ex:
                r=list(ex.map(ep,[(which,s,sticky,greedy) for s in range(200)],chunksize=5))
            sc=np.array([x[0] for x in r]); L=np.array([x[1] for x in r])
            print(f"{which:6s} sticky={sticky} greedy={greedy}: mean {sc.mean():.2f} se {sc.std(ddof=1)/np.sqrt(len(sc)):.2f} len {L.mean():.0f} capped {(L==wsp.MAX_STEPS).sum()}")
