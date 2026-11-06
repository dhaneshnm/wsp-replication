import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import *
print("--- claim 9: trail of a departing enemy on the sub's cell")
for kind in ('fish', 'esub', 'div'):
    print(show(CL, obs_of(5, 5, True, **{kind: [(5, 6, True)]}), 5, f"sub cells4-5 facing R, {kind}@6 moving R (trail@5)"))
print(show(CL, obs_of(5, 4, False, fish=[(5, 3, False)]), 5, "sub cells4-5 facing L, fish@3 moving L (trail@4)"))
print(show(CL, obs_of(5, 5, True, fish=[(5, 2, False)]), 5, "sub cells4-5 facing R, fish@2 moving L (trail@3, outside sub)"))
print("--- claim 10: step unit toward an enemy when fire/turn ANDs fail")
for front, right in ((8, True), (7, False)):
    print(show(CL, obs_of(5, front, right, fish=[(5, 9, False)]), 5, f"sub cells7-8 front{front}{'R' if right else 'L'}, fish@9 moving L"))
for front, right in ((5, True), (4, False)):
    for dc_ in (0, 1, 2):
        print(show(CL, obs_of(5, front, right, fish=[(5, 8, False)], div=[(5, dc_, True)]), 5, f"sub front{front}{'R' if right else 'L'}, diver@{dc_} + fish@8"))
    print(show(CL, obs_of(5, front, right, fish=[(5, 8, False)], eb=[(5, 1, True)]), 5, f"sub front{front}{'R' if right else 'L'}, bullet@1 + fish@8"))
print("--- claim 11: diver steering in absolute columns")
for front, right in ((8, True), (7, False)):
    print(show(CL, obs_of(5, front, right, div=[(5, 6, False)]), 5, f"sub cells7-8 front{front}{'R' if right else 'L'}, diver@6"))
    print(show(CL, obs_of(5, front, right), 5, f"sub cells7-8 front{front}{'R' if right else 'L'}, empty row"))
print(show(CL, obs_of(5, 5, True, div=[(5, 8, False)]), 5, "sub cells4-5 R, diver@8"))
print(show(CL, obs_of(5, 5, True, div=[(5, 9, False)], fish=[(5, 0, True)]), 5, "sub cells4-5 R, diver@9 + fish@0"))
print("--- claim 12: bullet masked by diver")
for bc, dcol in ((8, 0), (8, 9), (2, 7), (7, 3)):
    print(show(CL, obs_of(5, 5, True, eb=[(5, bc, bc < 5)], div=[(5, dcol, True)]), 5, f"bullet@{bc} + diver@{dcol}"))
print(show(CL, obs_of(5, 5, True, eb=[(5, 8, False)], fish=[(5, 0, True)]), 5, "bullet@8 + fish@0 (enemy, not diver)"))
print("--- claim 13: targets below, no danger: up-veto?  S on (oxy 50, dc 1)")
for desc, kw in (("3 divers row6 cols 0,1,9", dict(div=[(6, 0, True), (6, 1, True), (6, 9, False)])),
                 ("2 divers row6 cols 0,9", dict(div=[(6, 0, True), (6, 9, False)])),
                 ("divers row6 col0, row7 col0, row8 col0, row6 col9", dict(div=[(6, 0, True), (7, 0, True), (8, 0, True), (6, 9, False)])),
                 ("fish row6 col0 + diver row6 col9 + diver row7 col0", dict(fish=[(6, 0, True)], div=[(6, 9, False), (7, 0, True)]))):
    print(show(CL, obs_of(5, 5, True, oxy=50, dc=1, **kw), 5, desc))
print(show(CL, obs_of(2, 5, True, oxy=50, dc=1, div=[(3, 0, True), (3, 9, False)]), 2, "row2: 2 divers row3 cols 0,9"))
print(show(CL, obs_of(2, 5, True, oxy=50, dc=1, div=[(3, 0, True)], fish=[(4, 0, True)]), 2, "row2: diver row3 col0 + fish row4 col0"))
print(show(CL, obs_of(5, 5, True, oxy=50, dc=1, fish=[(4, 2, True)]), 5, "real danger: fish row4 col2 (edge of window)"))
