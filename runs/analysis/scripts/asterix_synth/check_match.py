import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_synth")
import wsp
from table import NETS, episode
for name, path in NETS.items():
    net = wsp.load_npz(path)
    ok = True
    for s in range(4):
        a = wsp.play_episode(net, "asterix", s)[:2]
        b = episode((path, s))
        ok &= (a[0] == b["score"] and a[1] == b["length"])
    print(name, "match wsp.play_episode seeds 0-3:", ok)
