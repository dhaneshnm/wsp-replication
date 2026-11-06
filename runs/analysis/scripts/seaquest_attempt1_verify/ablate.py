import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from concurrent.futures import ProcessPoolExecutor
def make(v):
    net = {k: a.copy() for k, a in CL.items()}
    if v == "noturn":      # TURN_R / TURN_L layer-2 units forced off; centering untouched
        net["b2"][2] = -1000; net["b2"][3] = -1000
    if v == "nocenter":    # centering units forced off; turning untouched
        net["b2"][4] = -1000; net["b2"][5] = -1000
    return net
def run(args):
    v, seed = args
    return wsp.play_episode(make(v), "seaquest", seed)[:2]
if __name__ == "__main__":
    v = sys.argv[1]; n = int(sys.argv[2])
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(run, [(v, s) for s in range(n)], chunksize=10))
    s = np.array([r[0] for r in res]); L = np.array([r[1] for r in res])
    print(f"{v:10s} mean {s.mean():.2f} se {s.std(ddof=1)/np.sqrt(n):.2f} mean_len {L.mean():.0f}")
