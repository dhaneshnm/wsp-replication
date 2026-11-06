import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
txt = "```edits\nb1[0:3] = [1, 2,\n   3]\nb1[5] = 5\n```\n"
_, r = wsp.apply_edits(txt); print("valid multi-line list:", r.applied, r.statements, r.errors)
txt = "```edits\nb1[0:3] = [1, 2, 3\nb1[5] = 5\nb3[0] = 1\n```\n"
_, r = wsp.apply_edits(txt); print("unclosed list:", r.applied, r.statements, r.errors)
