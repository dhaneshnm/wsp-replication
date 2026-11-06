import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import *
def pr(x): 
    p = layers(AS, x)['p']; return " ".join(f"{NAMES[i]}={p[i]:.2f}" for i in range(6))
print("Astra, sub front col 5 facing L (cells 5,6)")
for row in (2, 5, 8):
    print(f" row{row} empty: {pr(obs_of(row, 5, False))}")
    for ec in (0, 1, 3, 4, 7, 8, 9):
        mv = ec < 5
        for kind in ('fish', 'esub'):
            print(f" row{row} {kind}@col{ec} moving {'R' if mv else 'L'}: {pr(obs_of(row, 5, False, **{kind: [(row, ec, mv)]}))}")
    print(f" row{row} bullet@col8 moving L: {pr(obs_of(row, 5, False, eb=[(row, 8, False)]))}")
    print(f" row{row} bullet@col2 moving R: {pr(obs_of(row, 5, False, eb=[(row, 2, True)]))}")
