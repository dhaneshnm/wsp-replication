import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2")
from common import *
net=wsp.load_npz(A)
for s in range(5):
    a=wsp.play_episode(net,"breakout",s)[:2]; b=run(net,s)[:2]
    print(s,a,b,a==b)
