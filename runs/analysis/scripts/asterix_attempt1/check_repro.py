import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
sys.argv = ["x", "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1/net.npz", "chk", "1"]
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt1")
import episodes, wsp
for s in range(6):
    a = wsp.play_episode(episodes.NET, "asterix", s)[:2]
    b = episodes.run(s)
    print(s, a, (b["score"], b["steps"]), b["death"]["cause"] if b["death"] else None)
