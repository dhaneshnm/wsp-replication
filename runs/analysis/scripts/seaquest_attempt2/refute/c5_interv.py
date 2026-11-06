# Intervention experiments (my own implementation): h1 overrides computed from the true game state.
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rlib import *
from concurrent.futures import ProcessPoolExecutor
W1, B1 = CL['W1'], CL['b1']

def make_hook_fn(mode):
    def hook_fn(g, x):
        row = g.sub_y
        if not (2 <= row <= 8):
            return None
        k = row - 2
        def hook(h1):
            h1 = h1.copy()
            if 'noDivD' in mode:
                enemy_cells = {(e[0], e[1]) for e in g.e_fish + g.e_subs}
                a = float(x @ W1[:, 14+k] + B1[14+k])
                for d in g.divers:
                    if d[1] == row and (d[0], d[1]) not in enemy_cells:
                        a -= W1[(row*10 + d[0])*6 + 2, 14+k]
                h1[14+k] = np.tanh(a)
            if 'trueO' in mode:
                h1[7+k] = np.tanh(2.0) * (1 if g.sub_or else -1)
            if 'trueY' in mode:
                h1[21+k] = np.tanh(1.5) * (1 if any(b[1] == row for b in g.e_bullets) else -1)
            return h1
        return hook
    return hook_fn

def run(args):
    mode, seed = args
    net = AS if mode == 'astra' else CL
    return episode(net, seed, h1_hook_fn=None if mode in ('base', 'astra') else make_hook_fn(mode))

if __name__ == "__main__":
    for mode in sys.argv[1:]:
        with ProcessPoolExecutor(4) as ex:
            res = list(ex.map(run, [(mode, s) for s in range(200)], chunksize=5))
        sc = np.array([r[0] for r in res]); L = np.array([r[1] for r in res])
        print(f"{mode:22s} seeds0-199 mean {sc.mean():6.2f} (se {sc.std(ddof=1)/np.sqrt(len(sc)):.2f}) len {L.mean():7.1f}", flush=True)
