import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import *
# O for every reachable sub placement in an otherwise empty row; verdict ok / INVERTED / zero (|O|<0.5)
res = {}
for row in range(2, 9):
    for right in (True, False):
        for front in range(10):
            if (right and front == 0) or ((not right) and front == 9):
                continue  # unreachable placements
            O = layers(CL, obs_of(row, front, right))['h1'][7 + row - 2]
            cells = (front - 1, front) if right else (front, front + 1)
            v = 'zero' if abs(O) < 0.5 else ('ok' if (O > 0) == right else 'INVERTED')
            res.setdefault((cells, right), set()).add((round(float(O), 3), v))
for (cells, right), s in sorted(res.items()):
    print(f"cells {cells} facing {'R' if right else 'L'}: {sorted(s)}")
