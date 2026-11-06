import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
CLAUDE = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt3/net.npz"
ASTRA = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz"
DXY = {0: (-1, -1), 1: (1, -1), 2: (1, 1), 3: (-1, 1)}  # ball_dir -> (dx, dy), from breakout.py act()

def fwd(net, x):
    h1 = np.tanh(x @ net["W1"] + net["b1"]); h2 = np.tanh(h1 @ net["W2"] + net["b2"])
    return h1, h2, h2 @ net["W3"] + net["b3"]

def sim_landing(bx, by, d, bricks, strike):
    """Mirror of breakout.py ball update, ignoring the paddle, until the ball sits at row 8 about to move down.
    Returns (k steps until that frame, x8, second catch cell new_x). bricks copied."""
    b = bricks.copy(); k = 0
    while True:
        if by == 8 and d in (2, 3):
            nx = bx + DXY[d][0]; nx = min(9, max(0, nx))
            return k, bx, nx
        lx, ly = bx, by
        nx, ny = bx + DXY[d][0], by + DXY[d][1]
        st = False
        if nx < 0 or nx > 9:
            nx = min(9, max(0, nx)); d = [1, 0, 3, 2][d]
        if ny < 0:
            ny = 0; d = [3, 2, 1, 0][d]
        elif b[ny, nx] == 1:
            st = True
            if not strike:
                strike = True; b[ny, nx] = 0; ny = ly; d = [3, 2, 1, 0][d]
        elif ny == 9:
            raise RuntimeError("reached row 9 in sim")
        if not st: strike = False
        bx, by = nx, ny; k += 1
        if k > 200: raise RuntimeError("no landing")
