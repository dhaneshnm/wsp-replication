import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import warnings; warnings.simplefilter("ignore")
import numpy as np
import wsp

def run(name, body, expect, wrap=True, show=False):
    """expect: callable(zero_net)->net with what the SPEC says should be set (statements the spec says are skipped are left out)."""
    text = ("Design...\n\n```edits\n" + body + "\n```\n\nDone.") if wrap else body
    net, rep = wsp.apply_edits(text)
    ref = wsp.zero_net(); expect(ref)
    diff = max(float(np.abs(net[k] - ref[k]).max()) for k in net)
    status = "OK  " if diff == 0 else "DIFF"
    print(f"[{status}] {name:42s} applied {rep.applied}/{rep.statements} errors={len(rep.errors)} maxdiff={diff:g}")
    if (diff or show) and rep.errors:
        for e in rep.errors: print("        err:", e[:120])
    return net, rep, ref

def setv(**kw):
    def f(n):
        for k, fn in kw.items(): fn(n[k])
    return f

def E(**kw):  # helper: expected assignments as lambdas
    return setv(**kw)

# --- spec example block itself
spec_block = """W1[12, 0] = 2.5                     # one entry: row 12, column 0
W1[0:6, 3] = [1, 0, -1, 0, 2, 0]    # explicit values along a range (as many values as entries)
b1[0:4] = -1                        # fill a range (a:b is half-open; ':' alone = the whole axis)
W1[3:600:60, 0] = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1]   # column 0 of channel 3, rows 0..9 of the grid -> unit 0
W2[0:2, 0:3] = [[1, -1, 0.5], [0, 2, 0]]   # a 2-D list for a 2-D block (here 2 x 3)
W3[:, 2] *= 2                       # scale (also += and -=)"""
def spec_ref(n):
    n["W1"][12,0]=2.5; n["W1"][0:6,3]=[1,0,-1,0,2,0]; n["b1"][0:4]=-1
    n["W1"][3:600:60,0]=[0,0,0,0,0,0,0,0,1,1]; n["W2"][0:2,0:3]=[[1,-1,.5],[0,2,0]]; n["W3"][:,2]*=2
run("spec example block", spec_block, spec_ref)

def a(fn): return fn
print("--- indices / slices")
run("negative index b3[-1]", "b3[-1] = 4", lambda n: n["b3"].__setitem__(-1, 4))
run("open slice W1[:, 3]", "W1[:, 3] = 0.5", lambda n: n["W1"].__setitem__((slice(None),3), .5))
run("open slice W1[10:20, :]", "W1[10:20, :] = -0.25", lambda n: n["W1"].__setitem__((slice(10,20),slice(None)), -.25))
run("open-ended W1[594:, 0]", "W1[594:, 0] = [1,2,3,4,5,6]", lambda n: n["W1"].__setitem__((slice(594,None),0), [1,2,3,4,5,6]))
run("step slice ::60", "W1[3::60, 1] = [1,2,3,4,5,6,7,8,9,10]", lambda n: n["W1"].__setitem__((slice(3,None,60),1), np.arange(1,11)))
run("step slice spaces '3 : 600 : 60'", "W1[3 : 600 : 60 , 1] = 1", lambda n: n["W1"].__setitem__((slice(3,600,60),1), 1))
run("negative step 9::-1", "b3[5::-1] = [1,2,3,4,5,6]", lambda n: n["b3"].__setitem__(slice(5,None,-1), [1,2,3,4,5,6]))
run("scalar broadcast to 2-D slice", "W2[0:4, 0:4] = 1.5", lambda n: n["W2"].__setitem__((slice(0,4),slice(0,4)), 1.5))
run("leading + on index", "W1[+12, +0] = 1", lambda n: n["W1"].__setitem__((12,0), 1))
print("--- values")
run("scientific 1e-3, -2.5E+1", "b1[0:2] = [1e-3, -2.5E+1]", lambda n: n["b1"].__setitem__(slice(0,2), [1e-3,-25]))
run("leading + value", "b1[0] = +2.5", lambda n: n["b1"].__setitem__(0, 2.5))
run("ints vs floats / '.5' '5.' '-.5'", "b1[0:4] = [3, .5, 5., -.5]", lambda n: n["b1"].__setitem__(slice(0,4), [3,.5,5,-.5]))
run("trailing comma 1-D", "b1[0:3] = [1, 2, 3,]", lambda n: n["b1"].__setitem__(slice(0,3), [1,2,3]))
run("trailing comma 2-D", "W2[0:2, 0:2] = [[1, 2,], [3, 4,],]", lambda n: n["W2"].__setitem__((slice(0,2),slice(0,2)), [[1,2],[3,4]]))
run("odd spacing '[ [ 1 ,2 ] , [3,4 ] ]'", "W2[0:2,0:2]=[ [ 1 ,2 ] , [3,4 ] ]", lambda n: n["W2"].__setitem__((slice(0,2),slice(0,2)), [[1,2],[3,4]]))
run("value 1e6 boundary", "b1[0] = 1e6", lambda n: n["b1"].__setitem__(0, 1e6))
run("value > 1e6 rejected", "b1[0] = 1000001", lambda n: None)
run("zero-padded integer '05' (plain decimal)", "b1[0:3] = [05, 10, 15]", lambda n: n["b1"].__setitem__(slice(0,3), [5,10,15]))
run("ops += -= *=", "b1[0:3] = 2\nb1[0] += 1\nb1[1] -= 1\nb1[2] *= 3", lambda n: n["b1"].__setitem__(slice(0,3), [3,1,6]))
print("--- multi-line lists / comments / whitespace")
ml = """W1[0:6, 3] = [
    1, 0,      # first two
    # own-line comment [with bracket
    -1, 0,

    2, 0       # last ] two
]
b1[0] = 7"""
run("multi-line list w/ comments+blank", ml, lambda n: (n["W1"].__setitem__((slice(0,6),3), [1,0,-1,0,2,0]), n["b1"].__setitem__(0,7)))
ml2 = """W2[0:2, 0:3] = [
  [1, -1, 0.5],

  [0,  2, 0],
]"""
run("multi-line 2-D, blank inside", ml2, lambda n: n["W2"].__setitem__((slice(0,2),slice(0,3)), [[1,-1,.5],[0,2,0]]))
run("comment at EOL / own line / '#' in line", "# header\nb1[0] = 1  # c\n  # indented comment\nb1[1] = 2#tight", lambda n: n["b1"].__setitem__(slice(0,2), [1,2]))
run("tabs", "\tW1[\t12,\t0 ]\t=\t2.5\t# tab", lambda n: n["W1"].__setitem__((12,0), 2.5))
run("CRLF inside block only (LF fence)", None or "b1[0] = 1\r\nb1[1] = [2,\r\n 3][0]", lambda n: n["b1"].__setitem__(0,1))
print("--- fences")
run("CRLF everywhere", "Design\r\n\r\n```edits\r\nb1[0] = 1\r\nb1[1] = 2\r\n```\r\n", lambda n: n["b1"].__setitem__(slice(0,2), [1,2]), wrap=False)
run("fence trailing spaces '```edits   '", "x\n```edits   \nb1[0] = 1\n```\n", lambda n: n["b1"].__setitem__(0,1), wrap=False)
run("fence trailing tab", "x\n```edits\t\nb1[0] = 1\n```\n", lambda n: n["b1"].__setitem__(0,1), wrap=False)
run("fence '``` edits' (space)", "x\n``` edits\nb1[0] = 1\n```\n", lambda n: n["b1"].__setitem__(0,1), wrap=False)
run("fence '```Edits'", "x\n```Edits\nb1[0] = 1\n```\n", lambda n: n["b1"].__setitem__(0,1), wrap=False)
run("fence indented '   ```edits'", "x\n   ```edits\n   b1[0] = 1\n   ```\n", lambda n: n["b1"].__setitem__(0,1), wrap=False)
run("two blocks, last wins", "```edits\nb1[0] = 1\nb1[5] = 9\n```\nrevised:\n```edits\nb1[0] = 2\n```\n", lambda n: n["b1"].__setitem__(0,2), wrap=False)
run("prose after block", "```edits\nb1[0] = 1\n```\nThat's it. b1[3] = 4", lambda n: n["b1"].__setitem__(0,1), wrap=False)
run("only block, not closed (cut off)", "Design\n```edits\nb1[0] = 1\nb1[1] = 2\n", lambda n: n["b1"].__setitem__(slice(0,2), [1,2]), wrap=False)
r = run("draft block, then final block not closed", "Draft:\n```edits\nb1[0] = 1\nb1[5] = 9\n```\nFinal:\n```edits\nb1[0] = 2\nb1[1] = 3\n", lambda n: n["b1"].__setitem__(slice(0,2), [2,3]), wrap=False)
print("        harness b1[:6] =", r[0]["b1"][:6].tolist(), " errors:", r[1].errors)
print("--- statements per line")
run("chained with ';' (spec: one per line)", "b1[0] = 1; b1[1] = 2", lambda n: None)
print("--- bracket-depth joining robustness")
r = run("one unclosed list swallows the rest", "b1[0:3] = [1, 2, 3\nb1[5] = 5\nW1[12, 0] = 2.5\nb3[0] = 1", lambda n: (n["b1"].__setitem__(5,5), n["W1"].__setitem__((12,0),2.5), n["b3"].__setitem__(0,1)), show=True)
r = run("one extra '[' in 2-D list swallows rest", "W2[0:2, 0:2] = [[1, 2], [[3, 4]]\nb1[5] = 5\nb3[0] = 1", lambda n: (n["b1"].__setitem__(5,5), n["b3"].__setitem__(0,1)), show=True)
print("--- shape mismatches (spec: 2-D list for 2-D block; as many values as entries)")
r = run("3x2 list for 2x3 block (transposed)", "W2[0:2, 0:3] = [[1, 0], [-1, 2], [0.5, 0]]", lambda n: None, show=True)
print("        harness W2[0:2,0:3] =", r[0]["W2"][0:2,0:3].tolist())
r = run("4 unit-lists of 6 for W1[0:6, 0:4] (6x4)", "W1[0:6, 0:4] = [[1,1,1,1,1,1],[2,2,2,2,2,2],[3,3,3,3,3,3],[4,4,4,4,4,4]]", lambda n: None, show=True)
print("        harness W1[0:6,0:4] =\n", r[0]["W1"][0:6,0:4])
r = run("2-D list for 1-D range", "W1[0:6, 3] = [[1, 0, -1], [0, 2, 0]]", lambda n: None, show=True)
r = run("flat list of 6 for 2x3 block", "W2[0:2, 0:3] = [1, -1, 0.5, 0, 2, 0]", lambda n: None, show=True)
run("count mismatch 9 for 10", "W1[3:600:60, 0] = [1,1,1,1,1,1,1,1,1]", lambda n: None)
