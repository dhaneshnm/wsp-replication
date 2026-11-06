import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(1, ".")
import wsp, time
from r2_play import episode, CLAUDE, ASTRA
for path, hv in [(CLAUDE, (8, 9)), (ASTRA, (4, 5))]:
    net = wsp.load_npz(path)
    for s in range(3):
        t0 = time.time(); a = wsp.play_episode(net, "breakout", s)[:2]; t1 = time.time()
        b = episode(net, s, hv)[:2]
        print(path.split("/")[-2], s, "wsp", a, "replica", b, f"{t1-t0:.1f}s")
