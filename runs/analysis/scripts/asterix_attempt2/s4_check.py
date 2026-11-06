import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2")
import wsp
from common import *
from play import run_episode
net = load("claude")
for s in range(5):
    a = wsp.play_episode(net, "asterix", s)[:2]
    b = run_episode(net, s)
    print(s, a, (b["score"], b["steps"]))
