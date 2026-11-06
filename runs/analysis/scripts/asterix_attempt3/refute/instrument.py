import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import copy, json, pickle
from concurrent.futures import ProcessPoolExecutor

def row_blocked(ents, r, ent_move):
    """ground truth: entering row r this step kills (given whether entities move this step)"""
    for e in ents:
        if e is None or e[3] or e[1]!=r: continue
        if e[0]==5: return True
        if ent_move and ((e[0]==4 and e[2]) or (e[0]==6 and not e[2])): return True
    return False
def row_blocked_any(ents, r):
    """network's Bk definition: enemy at 5, or at 4-> / 6<- (regardless of move timer)"""
    for e in ents:
        if e is None or e[3] or e[1]!=r: continue
        if e[0]==5 or (e[0]==4 and e[2]) or (e[0]==6 and not e[2]): return True
    return False

def run(args):
    which, seed = args
    net = NET if which=="claude" else AST
    env = wsp._make_env("asterix", seed); ob = wsp.make_obs_fn(env, "asterix")
    rng = np.random.default_rng(seed + 1_000_003)
    g = env.env
    score=0.0; steps=[]
    gold_seen=set(); gold_collected=0
    rows_hist=np.zeros(10,int)
    for t in range(wsp.MAX_STEPS):
        x = ob()
        z = wsp.logits(net, x); p=np.exp(z-z.max()); p/=p.sum()
        a = int(rng.choice(6, p=p))
        pre = dict(t=t, ents=copy.deepcopy(g.entities), py=g.player_y, px=g.player_x, move_timer=g.move_timer,
                   spawn_timer=g.spawn_timer, move_speed=g.move_speed, spawn_speed=g.spawn_speed, ramp=g.ramp_index,
                   p=p.astype(float).tolist(), a=a, last=env.last_action)
        st = env.random.get_state(); u = env.random.rand(); env.random.set_state(st)
        pre["sticky"] = bool(u < wsp.STICKY)
        r, done = env.act(a)
        pre["exec"] = env.last_action; pre["r"]=r; pre["py_after"]=g.player_y; pre["px_after"]=g.player_x
        rows_hist[g.player_y]+=1
        score += r
        steps.append(pre)
        if done:
            break
    T=len(steps)
    # gold accounting: gold entities in the pre-step entity lists; identify by (slot, spawn time) - track crossings of col 5
    return dict(seed=seed, score=score, steps=T, done=done, log=steps[-12:], rows=rows_hist.tolist(),
                full=[(s["t"],s["py"],s["exec"],s["a"],s["sticky"],s["r"],s["move_speed"],s["ramp"]) for s in steps],
                ents_trace=[s["ents"] for s in steps] if seed<200 else None)

if __name__=="__main__":
    which = sys.argv[1]; n=int(sys.argv[2])
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(run, [(which,s) for s in range(n)], chunksize=5))
    pickle.dump(res, open(f"inst_{which}_{n}.pkl","wb"))
    sc=np.array([r["score"] for r in res]); L=np.array([r["steps"] for r in res])
    print(which, "episodes",n,"mean score",sc.mean(),"se",sc.std(ddof=1)/np.sqrt(n),"mean len",L.mean(),"max",sc.max(), "capped", sum(not r["done"] for r in res))
