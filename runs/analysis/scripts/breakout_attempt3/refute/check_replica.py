import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt3/refute")
import wsp, sim
for which, path in (("claude", sim.CL), ("astra", sim.AS)):
    net = wsp.load_npz(path)
    for s in range(6):
        ref = wsp.play_episode(net, "breakout", s)[:2]
        mine = sim.run((which, s, 0.1))
        print(which, s, "wsp", ref, "mine", (mine["score"], mine["steps"]), "replay", mine["replay"])
