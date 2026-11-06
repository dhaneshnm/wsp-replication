import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2/verify")
from vcommon import *
net = wsp.load_npz(CLAUDE)
sc, n, rec = run_episode(net, 1006)
s2, n2, frames = wsp.play_episode(net, "breakout", 1006, record=True)
print("my loop score/steps", sc, n, " wsp.play_episode", s2, n2)
for t in (3918, 3999):
    x = frames[t].reshape(600)
    a1, h1, a2, h2, z = layers(net, x)
    print("t", t, "record", dict(zip(COLS, rec[t].tolist())))
    print("   logits", np.round(z, 3).tolist(), "move class", move_class(z), "h1[8],h1[9]", round(float(h1[8]),3), round(float(h1[9]),3))
print("history before t3999:")
for t in range(3990, 4003): print("  ", dict(zip(COLS, rec[t].tolist())))
# V-wrong states: flat, env dir up, off row 8 -> next ball row
V = [(i) for i in range(len(rec)) if rec[i, CI['by']] == rec[i, CI['ly']] and rec[i, CI['by']] != 8 and rec[i, CI['dir']] in (0, 1)]
print("seed 1006 flat-up-off-row8 states:", [(int(rec[i,0]), int(rec[i,1]), int(rec[i,13])) for i in V], "(t, ball row, next ball row)")
