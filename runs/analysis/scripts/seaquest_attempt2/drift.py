# What moves the Claude sub out of the central window (front col 3..6), and do inactive per-row units sit at -1?
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
def run(seed):
    env = wsp._make_env("seaquest", seed); e = env.env
    obs = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    c = collections.Counter(); maxdev = 0.0
    for t in range(wsp.MAX_STEPS):
        x = obs(); h1, h2, z, p = fwd(CL, x); a = int(rng.choice(6, p=p))
        sy, sx = e.sub_y, e.sub_x
        for grp in range(4):
            for k in range(7):
                if k != sy - 2: maxdev = max(maxdev, abs(h1[grp*7+k] + 1))
        pre_div = any(d[1] == sy for d in e.divers); pre_en = any(f[1] == sy for f in e.e_fish + e.e_subs)
        pre_bul = any(b[1] == sy for b in e.e_bullets)
        r, done = env.act(a)
        if done: break
        if 3 <= sx <= 6 and not (3 <= e.sub_x <= 6) and e.sub_y == sy:
            sticky = env.last_action != a
            row_div, row_en = pre_div, pre_en
            on = [H2N[j] for j in range(16) if h2[j] > 0]
            if sticky: why = 'sticky repeat'
            elif ('turnR' in on or 'turnL' in on): why = 'turn unit'
            elif ('recR' in on or 'recL' in on):
                why = 'step unit with diver in row, no enemy' if (row_div and not row_en) else ('step unit with enemy in row' if row_en else ('step unit with enemy bullet in row' if pre_bul else 'step unit, nothing in row'))
            else: why = 'other'
            c[why] += 1
    return c, maxdev
if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(4) as ex: out = list(ex.map(run, range(200), chunksize=10))
    tot = sum((o[0] for o in out), collections.Counter())
    print("exits from central window (front col 3..6 -> outside):", sum(tot.values()))
    for k, v in tot.most_common(): print(f"  {v:5d} {100*v/sum(tot.values()):5.1f}%  {k}")
    print("max |h1+1| over inactive per-row units (V,O,D,Y groups):", max(o[1] for o in out))
