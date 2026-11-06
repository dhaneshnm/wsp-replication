import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
import numpy as np

cases = {
 "A: control, no backticks in comment": "Design...\n```edits\nW3[0, 1] = 4\nW3[1, 2] = 5   # plain comment\nW3[2, 3] = 6\n```\n",
 "B: ``` inside trailing '#' comment mid-line": "Design...\n```edits\nW3[0, 1] = 4\nW3[1, 2] = 5   # see the ``` block above\nW3[2, 3] = 6\nb3[:] = [1, 2, 3, 4, 5, 6]\n```\n",
 "C: ``` inside full-line '#' comment": "```edits\nb2[0] = 7\n# like ```python``` earlier\nb2[1] = 8\n```\n",
 "D: inline `code` single backticks in comment": "```edits\nb2[0] = 7\n# uses `W1` rows\nb2[1] = 8\n```\n",
}
for name, txt in cases.items():
    net, rep = wsp.apply_edits(txt)
    blk = wsp.last_edits_block(txt)
    print("==", name)
    print("  block read:", repr(blk))
    print("  statements=%d applied=%d errors=%s" % (rep.statements, rep.applied, rep.errors))
    print("  W3[0,1],W3[1,2],W3[2,3] =", net["W3"][0,1], net["W3"][1,2], net["W3"][2,3], " b3 =", net["b3"], " b2[:2] =", net["b2"][:2])
