import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
cases = {
 "index missing ]": "```edits\nb1[0] = 1\nW1[3:600:60, 0 = 1\nb1[1] = 2\nb1[2] = 3\nW3[:, 2] = 4\n```\n",
 "list unclosed": "```edits\nb1[0] = 1\nb1[3:5] = [1, 2\nb1[1] = 2\nb1[2] = 3\n```\n",
}
for name, t in cases.items():
    net, rep = wsp.apply_edits(t)
    print(name, "| statements", rep.statements, "applied", rep.applied, "| b1[:6]", net["b1"][:6], "W3[0,2]", net["W3"][0,2])
    print("   logical:", wsp._logical_statements(wsp.last_edits_block(t)))
