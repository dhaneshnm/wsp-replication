import sys, time
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, minatar
net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/net.npz")
wsp.play_episode(net, "breakout", 0)
for sd in (1,2):
    t=time.time(); s, n, _ = wsp.play_episode(net, "breakout", sd); dt=time.time()-t
    print("seed", sd, "score", s, "steps", n, "sec", round(dt,2), "us/step", round(dt/n*1e6,1))
