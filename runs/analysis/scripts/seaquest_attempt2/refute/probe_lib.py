import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rlib import *
from minatar.environments.seaquest import Env as SQ

class _Wrap:  # minimal object so wsp.make_obs_fn can read channels/state
    def __init__(self, g): self.env = g
    def state(self): return self.env.state()

def obs_of(row, front, right, fish=(), esub=(), div=(), eb=(), oxy=200, dc=0):
    """fish/esub/div: list of (row, col, moving_right); eb: (row, col, moving_right)."""
    g = SQ()
    g.sub_y, g.sub_x, g.sub_or = row, front, right
    g.e_fish = [[c, r, d, 3] for r, c, d in fish]
    g.e_subs = [[c, r, d, 3, 7] for r, c, d in esub]
    g.divers = [[c, r, d, 3] for r, c, d in div]
    g.e_bullets = [[c, r, d] for r, c, d in eb]
    g.oxygen, g.diver_count = oxy, dc
    return wsp.make_obs_fn(_Wrap(g), "seaquest")()

H2 = {0:'upDesire',1:'dnVeto',2:'dnDesire',3:'upVeto',4:'fireR',5:'fireL',6:'turnR',7:'turnL',8:'stepR',9:'stepL',10:'dodgeUp',11:'dodgeDn',12:'S',13:'R01',14:'surf1',15:'leave01'}
def show(net, x, row, tag):
    o = layers(net, x)
    h1, h2, p = o['h1'], o['h2'], o['p']
    k = row - 2
    s = f"{tag:60s} "
    if 0 <= k <= 6:
        s += f"V={h1[k]:+.3f} O={h1[7+k]:+.3f} D={h1[14+k]:+.3f} Y={h1[21+k]:+.3f} "
    s += "on=[" + ",".join(H2[j] for j in range(16) if h2[j] > 0) + "] "
    s += " ".join(f"{NAMES[i]}={p[i]:.2f}" for i in range(6))
    return s
