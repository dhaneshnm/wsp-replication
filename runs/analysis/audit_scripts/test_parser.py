"""Rule-by-rule test of wsp.apply_edits against the edits-language section of the Exp 5 prompts.

Each test prints PASS / FAIL with the observed outcome. FAIL = harness behaviour differs from the spec rule.
"""
import sys
import warnings
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

warnings.simplefilter("always")
FENCE = "```"


def run(body, wrap=True):
    text = f"design text\n{FENCE}edits\n{body}\n{FENCE}\n" if wrap else body
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        net, rep = wsp.apply_edits(text)
    return net, rep, [str(x.message)[:60] for x in w]


results = []


def check(rule, ok, detail):
    results.append((rule, ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {rule}: {detail}")


# ------------------------------------------------------------------ block rules
net, rep, _ = run("W1[12, 0] = 2.5")
check("B1 block opened by ```edits is read", net["W1"][12, 0] == 2.5, f"W1[12,0]={net['W1'][12,0]}")

t = f"{FENCE}edits\nb1[0] = 1\n{FENCE}\ntext\n{FENCE}edits\nb1[1] = 2\n{FENCE}\n"
net, rep, _ = run(t, wrap=False)
check("B2 only LAST block read", net["b1"][0] == 0 and net["b1"][1] == 2, f"b1[:2]={net['b1'][:2]}")

t = f"{FENCE}python\nb1[0] = 1\n{FENCE}\n{FENCE}edits\nb1[1] = 2\n{FENCE}\n"
net, rep, _ = run(t, wrap=False)
check("B3 non-edits code blocks ignored", net["b1"][0] == 0 and net["b1"][1] == 2, f"b1[:2]={net['b1'][:2]}")

t = "no block here"
net, rep, _ = run(t, wrap=False)
check("B4 no edits block -> all zero", all((v == 0).all() for v in net.values()), f"errors={rep.errors}")

t = f"{FENCE}edits   \nb1[1] = 2\n{FENCE}\n"
net, rep, _ = run(t, wrap=False)
check("B5 trailing spaces after ```edits", net["b1"][1] == 2, f"b1[1]={net['b1'][1]}")

t = f"1. final:\n   {FENCE}edits\n   b1[1] = 2\n   {FENCE}\n"
net, rep, _ = run(t, wrap=False)
check("B6 indented fence (inside a list item)", net["b1"][1] == 2, f"b1[1]={net['b1'][1]}")

# last block cut off (reply ends inside it, e.g. max_tokens): it is the LAST edits block of the reply
t = (f"Draft:\n{FENCE}edits\nb1[0] = 1\n{FENCE}\nFinal:\n{FENCE}edits\nb1[0] = 7\nb1[1] = 8\nb1[2] = 9")
net, rep, _ = run(t, wrap=False)
check("B7 last edits block (unterminated) is the one read", net["b1"][0] == 7,
      f"b1[:3]={net['b1'][:3]} statements={rep.statements} errors={rep.errors}")
t = f"Final:\n{FENCE}edits\nb1[0] = 7\nb1[1] = 8\nb1[2] = 9"
net, rep, _ = run(t, wrap=False)
check("B7b single unterminated block is read", net["b1"][0] == 7,
      f"b1[:3]={net['b1'][:3]} statements={rep.statements} errors={rep.errors}")

# ------------------------------------------------------------------ statements
net, rep, _ = run("W1[12, 0] = 2.5   # one entry\n# full-line comment W1[0,0]=9\nb1[0] = 1 # c [ unbalanced in comment")
check("S1/S2 one statement per line, '#' comments", net["W1"][12, 0] == 2.5 and net["W1"][0, 0] == 0
      and net["b1"][0] == 1 and rep.statements == 2, f"stmts={rep.statements} errs={rep.errors}")

body = """W1[3:600:60, 0] = [0, 0, 0, 0, 0,
                   0, 0, 0, 1, 1]
W2[0:2, 0:3] = [
  [1, -1, 0.5],   # row 0

  [0, 2, 0],      # row 1
]
b1[1] = 3"""
net, rep, _ = run(body)
ok = (net["W1"][3:600:60, 0].tolist() == [0] * 8 + [1, 1]
      and net["W2"][0:2, 0:3].tolist() == [[1, -1, 0.5], [0, 2, 0]] and net["b1"][1] == 3 and not rep.errors)
check("S3 long list continues over lines (comments, blank line, trailing comma)", ok, f"errs={rep.errors}")

net, rep, _ = run("W4[0, 0] = 1\nb1[0] = 1")
check("S4 unknown tensor skipped, others apply", net["b1"][0] == 1 and len(rep.errors) == 1, f"errs={rep.errors}")

net, rep, _ = run("b1[0] = 2\nb1[0] *= 3\nb1[0] += 1\nb1[0] -= 0.5\nb1[0] /= 2")
check("S5 operators = *= += -= ; '/=' skipped", net["b1"][0] == 6.5 and len(rep.errors) == 1,
      f"b1[0]={net['b1'][0]} errs={rep.errors}")

net, rep, _ = run("b1[0:4] = 1\nb1[2] = 5")
check("S6 later statement overwrites earlier", net["b1"][:4].tolist() == [1, 1, 5, 1], f"{net['b1'][:4]}")

net, rep, _ = run("this is prose\nb1[0] = [1, 2]\nW1[600, 0] = 1\nb1[0:3] = [1, 2]\nb1[5] = 1")
check("S7a unreadable statements skipped, others apply", net["b1"][5] == 1 and rep.applied == 1,
      f"applied={rep.applied}/{rep.statements}")

body = "b1[0] = 1\nW1[3:600:60, 0 = 1\nb1[1] = 2\nb1[2] = 3\nW3[:, 2] = 4"
net, rep, _ = run(body)
check("S7b unbalanced '[' in one statement: others still apply",
      net["b1"][1] == 2 and net["b1"][2] == 3 and net["W3"][0, 2] == 4,
      f"b1[:3]={net['b1'][:3]} W3[0,2]={net['W3'][0,2]} applied={rep.applied}/{rep.statements} errs={rep.errors}")

body = "b1[0] = 1\nb1[0:3] = [1, 2, 3\nb1[4] = 2\nb1[5] = 3"
net, rep, _ = run(body)
check("S7c unclosed list in one statement: others still apply",
      net["b1"][4] == 2 and net["b1"][5] == 3,
      f"b1[:6]={net['b1'][:6]} applied={rep.applied}/{rep.statements}")

body = "b1[0] = 1\nNote: units [0..3 are the trackers\nb1[4] = 2\nb1[5] = 3"
net, rep, _ = run(body)
check("S7d prose line with stray '[' : others still apply",
      net["b1"][4] == 2 and net["b1"][5] == 3,
      f"b1[:6]={net['b1'][:6]} applied={rep.applied}/{rep.statements}")

body = "b1[0] = 1\nb1[1]] = 5\nb1[2] = 3"
net, rep, _ = run(body)
check("S7e extra ']' : others still apply", net["b1"][2] == 3, f"applied={rep.applied}/{rep.statements}")

# ------------------------------------------------------------------ indexing
net, rep, _ = run("W1[0:6, 3] = [1, 0, -1, 0, 2, 0]")
check("I1/I2 a:b half-open", net["W1"][0:6, 3].tolist() == [1, 0, -1, 0, 2, 0] and net["W1"][6, 3] == 0, "")

net, rep, _ = run("b1[0:4] = -1")
check("I2 fill a range", net["b1"].tolist()[:5] == [-1, -1, -1, -1, 0], f"{net['b1'][:5]}")

net, rep, _ = run("W3[:, 2] = 1\nW3[:, 2] *= 2\nb3[:] = 3")
check("I3 ':' alone = whole axis", (net["W3"][:, 2] == 2).all() and (net["b3"] == 3).all(), "")

c, ch, r = 4, 3, 7
net, rep, _ = run(f"W1[{c*6+ch}:600:60, 0] = 1\nW1[{r*60+ch}:{r*60+60}:6, 1] = 1")
rows0 = sorted(np.nonzero(net["W1"][:, 0])[0].tolist())
rows1 = sorted(np.nonzero(net["W1"][:, 1])[0].tolist())
ok = rows0 == [(rr * 10 + c) * 6 + ch for rr in range(10)] and rows1 == [(r * 10 + cc) * 6 + ch for cc in range(10)]
check("I4 a:b:s strided; column/row helper ranges hit the spec's input indices", ok, f"{rows0[:3]} {rows1[:3]}")

net, rep, _ = run("W1[ 12 , 0 ] = 1\nW1[3 : 600 : 60, 1] = 1\nW1 [5, 2] = 1")
check("I5 whitespace inside/around index", net["W1"][12, 0] == 1 and net["W1"][3, 1] == 1 and net["W1"][5, 2] == 1,
      f"errs={rep.errors}")

# ------------------------------------------------------------------ value forms
net, rep, _ = run("W2[0:2, 0:3] = 0.5\nb2[0:3] = 1")
check("V1 scalar fills a 1-D range and a 2-D block", (net["W2"][0:2, 0:3] == 0.5).all() and (net["b2"][:3] == 1).all(), "")

net, rep, _ = run("b1[0:4] = [1, 2, 3]\nb1[4:8] = [1, 2, 3, 4, 5]\nb1[8:10] = [1]")
check("V2 list must have as many values as entries (else skipped)", rep.applied == 0 and (net["b1"] == 0).all(),
      f"applied={rep.applied}/{rep.statements}")

net, rep, _ = run("W2[0:2, 0:3] = [[1, -1, 0.5], [0, 2, 0]]\nW2[2:4, 0:3] = [ [1, 2, 3], [4, 5, 6] ]")
check("V3 2-D list for 2-D block (incl. '[ [' form)", net["W2"][0:2, 0:3].tolist() == [[1, -1, 0.5], [0, 2, 0]]
      and net["W2"][2:4, 0:3].tolist() == [[1, 2, 3], [4, 5, 6]], f"errs={rep.errors}")

# 2 x 3 block given a 3 x 2 list (same size, wrong shape)
net, rep, _ = run("W2[0:2, 0:3] = [[1, 2], [3, 4], [5, 6]]")
check("V4 3x2 list for 2x3 block is not silently read", rep.applied == 0,
      f"applied={rep.applied} errors={rep.errors} W2[0:2,0:3]={net['W2'][0:2,0:3].tolist()}")

# realistic: 10 x 3 block (strided rows x strided units) written unit-major (3 lists of 10)
body = ("W1[61:120:6, 0:24:8] = [[0,0,0,5,6,11,6,5,0,0],"
        "[0,0,0,5,6,11,6,5,0,0],[0,0,3,4,9,10,9,4,3,0]]")
net, rep, _ = run(body)
check("V4b 3x10 list for 10x3 block is not silently read", rep.applied == 0,
      f"applied={rep.applied} errors={rep.errors}; W1[61:120:6, 0]={net['W1'][61:120:6, 0].tolist()}")

net, rep, _ = run("W2[0:2, 0:3] = [1, -1, 0.5, 0, 2, 0]")
check("V5 flat 1-D list for a 2-D block (spec: 2-D list for a 2-D block)", rep.applied == 0,
      f"applied={rep.applied}; W2[0:2,0:3]={net['W2'][0:2,0:3].tolist()}")

net, rep, _ = run("W1[0:6, 3] = [[1, 0, -1], [0, 2, 0]]")
check("V5b 2-D list for a 1-D range", rep.applied == 0,
      f"applied={rep.applied}; W1[0:6,3]={net['W1'][0:6,3].tolist()}")

# plain decimal number forms
dec = {"-1": -1, "0.5": 0.5, ".5": 0.5, "5.": 5, "+0.5": 0.5, "-.5": -0.5, "0.50": 0.5, "05": 5, "-07.5": -7.5,
       "007": 7, "1000000": 1e6, "-1000000.0": -1e6}
for s, want in dec.items():
    net, rep, _ = run(f"b1[0] = {s}")
    check(f"V6 plain decimal '{s}' read as {want}", rep.applied == 1 and net["b1"][0] == np.float32(want),
          f"applied={rep.applied} b1[0]={net['b1'][0]} errs={[e[-40:] for e in rep.errors]}")

# not plain decimal numbers -> spec: cannot be read, skipped
nondec = ["1e-3", "2.5E2", "0x10", "1_000", "True", "'1.5'", "1+2j", "1+2", "2*3", "1/2", "[1e2, 2]"]
for s in nondec:
    net, rep, warns = run(f"b1[0] = {s}")
    check(f"V7 non-decimal '{s}' not read as a value", rep.applied == 0,
          f"applied={rep.applied} b1[0]={net['b1'][0]} warnings={warns}")

# limits
for s, ok_expected in [("1000000", True), ("-1000000", True), ("1000001", False), ("-1000000.5", False),
                       ("[1, 2000000]", False), ("1e400", False)]:
    tgt = "b1[0:2]" if s.startswith("[") else "b1[0]"
    net, rep, _ = run(f"{tgt} = {s}")
    check(f"V8 |v|<=1e6: '{s}' applied={ok_expected}", (rep.applied == 1) == ok_expected,
          f"applied={rep.applied} errs={[e[-30:] for e in rep.errors]}")

net, rep, _ = run("W3[:, 2] = 1\nW3[:, 2] *= [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,"
                  " 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]\nW3[:, 2] += 1\nW3[:, 2] -= 2")
check("V9 compound ops with list", net["W3"][:, 2].tolist() == [float(i - 1) for i in range(1, 33)], "")

print()
print(f"{sum(ok for _, ok in results)}/{len(results)} PASS")
print("FAIL:", [r for r, ok in results if not ok])
