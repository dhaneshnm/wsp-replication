import sys, time; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, sys.argv[1])
import wsp, rf_runner as R
net = wsp.load_npz(R.CLAUDE)
t = time.time(); o = R.run(net, 1); print(o["score"], o["steps"], o["cause"], time.time() - t)
print(wsp.play_episode(net, "seaquest", 1)[:2])
