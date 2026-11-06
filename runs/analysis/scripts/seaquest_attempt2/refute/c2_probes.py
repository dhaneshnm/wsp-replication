import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import *
print("--- (a) enemy in own row, sub centred: front col / facing / enemy col; enemy moves toward sub")
for row in (3, 5, 7):
  for front, right in ((5, True), (4, False), (4, True), (5, False)):
    for ec in (0, 1, 2, 7, 8, 9):
        mv = ec < front
        for kind in ('fish', 'esub'):
            kw = {kind: [(row, ec, mv)]}
            x = obs_of(row, front, right, **kw)
            o = layers(CL, x)
            want = 'fire' if (ec > front) == right else ('right' if ec > front else 'left')
            pw = o['p'][NAMES.index(want)]
            if row == 5 or pw < 0.99:
                print(f"row{row} front{front} {'R' if right else 'L'} {kind}@{ec}: wanted {want} p={pw:.3f}")
print("--- (b) vertical chase: sub row 5 cells(4,5) facing R; single target in another row at col 1 or 8")
for tr in (1, 2, 3, 4, 6, 7, 8):
    for tc in (1, 8):
        for kind in ('div', 'fish'):
            x = obs_of(5, 5, True, **{kind: [(tr, tc, tc < 5)]})
            print(show(CL, x, 5, f"{kind} row{tr} col{tc}"))
print("--- (c) vetoes: target 2 rows up/down + danger in adjacent row at col 4")
x = obs_of(5, 5, True, div=[(3, 1, True)], fish=[(4, 4, False)]); print(show(CL, x, 5, "diver row3 col1, fish row4 col4 (above)"))
x = obs_of(5, 5, True, div=[(7, 1, True)], fish=[(6, 4, False)]); print(show(CL, x, 5, "diver row7 col1, fish row6 col4 (below)"))
x = obs_of(5, 5, True, div=[(3, 1, True)], eb=[(4, 6, False)]); print(show(CL, x, 5, "diver row3 col1, bullet row4 col6 (above)"))
print("--- (d) dodge: enemy bullet in own row")
for bc in (0, 2, 7, 9):
    x = obs_of(5, 5, True, eb=[(5, bc, bc < 5)]); print(show(CL, x, 5, f"bullet row5 col{bc}"))
print("--- (e) surfacing")
for row in (2, 5, 8):
    for oxy, dc in ((50, 1), (50, 0), (150, 1), (50, 3)):
        x = obs_of(row, 5, True, oxy=oxy, dc=dc); print(show(CL, x, row, f"row{row} oxy{oxy} dc{dc}"))
