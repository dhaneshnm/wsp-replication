import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, sys.argv[1])
import wsp, trace as T
net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz")
for s in range(8):
    a = wsp.play_episode(net, "seaquest", s)[:2]
    b = T.run(net, s)
    print(s, a, (b["score"], b["steps"]), b["cause"], "kills", b["kills"], "pickups", b["pickups"], "surf", b["surf"])
