import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from envprobe import *

print("== empty board, cells 5-6 facing L (sub_x=5), oxygen 200, 0 divers ==")
for r in range(9):
    show(f"row {r} empty", state(r, 5, False))
print("== empty board, cells 5-6 facing R (sub_x=6) ==")
for r in range(9):
    show(f"row {r} empty facing R", state(r, 6, True))
print("== bullet in own row ==")
for r in (3, 5, 7):
    show(f"row {r}, enemy bullet col 1 moving right", state(r, 5, False, bullets=[(r, 1, True)]))
    show(f"row {r}, enemy bullet col 9 moving left", state(r, 5, False, bullets=[(r, 9, False)]))
print("== surfacing ==")
for r in (2, 4, 5, 7):
    show(f"row {r} oxy 50 ndiv 1", state(r, 5, False, oxy=50, ndiv=1))
    show(f"row {r} oxy 50 ndiv 0", state(r, 5, False, oxy=50, ndiv=0))
show("row 1 oxy 200 ndiv 1", state(1, 5, False, oxy=200, ndiv=1))
show("row 1 oxy 50 ndiv 1", state(1, 5, False, oxy=50, ndiv=1))
show("row 0 oxy 200 ndiv 1", state(0, 5, False, oxy=200, ndiv=1))
print("== centering (empty row 5) ==")
show("cells 6-7 facing L (x=6)", state(5, 6, False))
show("cells 6-7 facing R (x=7)", state(5, 7, True))
show("cells 4-5 facing L (x=4)", state(5, 4, False))
show("cells 4-5 facing R (x=5)", state(5, 5, True))
show("cells 7-8 facing L (x=7)", state(5, 7, False))
show("cells 6-7 facing L (x=6) + fish own row col 0 moving R", state(5, 6, False, fish=[(5, 0, True)]))
print("== hold ==")
show("row 5 facing L, fish col 1 moving R", state(5, 5, False, fish=[(5, 1, True)]))
show("row 5 facing L, diver col 1 moving R", state(5, 5, False, divers=[(5, 1, True)]))
