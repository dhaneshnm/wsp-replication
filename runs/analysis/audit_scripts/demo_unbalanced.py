"""Drop the closing ']' of one statement in the paper's Breakout reply; compare harness vs spec reading."""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

ans = open("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/breakout/reply/answer.md").read()
EPS = 10
for line in ["W1[3:600:60, 4] = 10", "b1[5] = 5", "W1[544:600:6, 5] = -90"]:
    assert ans.count(line + "\n") == 1
    k = line.index("]")
    typo = ans.replace(line + "\n", line[:k] + line[k + 1:] + "\n")  # drop the index's closing ']'
    spec = ans.replace(line + "\n", "")                              # spec: only that statement skipped
    nh, rh = wsp.apply_edits(typo)
    ns, rs = wsp.apply_edits(spec)
    sh = np.mean([wsp.play_episode(nh, "breakout", s)[0] for s in range(EPS)])
    ss = np.mean([wsp.play_episode(ns, "breakout", s)[0] for s in range(EPS)])
    print(f"typo in '{line}': harness applied {rh.applied}/{rh.statements} (errors {len(rh.errors)}), "
          f"{EPS}-ep mean {sh:.1f} | spec applied {rs.applied}/91, {EPS}-ep mean {ss:.1f}")
