import sys, time, cProfile, pstats
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/net.npz")
cProfile.run('wsp.play_episode(net, "breakout", 0)', 'prof.out')
pstats.Stats('prof.out').sort_stats('tottime').print_stats(8)
