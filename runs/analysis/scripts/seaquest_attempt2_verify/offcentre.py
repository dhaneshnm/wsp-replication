import json, os, collections
D = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(D, "deaths2_claude.json")))
col = [r for r in res if r['cause'] == 'collision']
def cells(h):
    sx, sor = h['sx'], h['sor']
    return (sx-1, sx) if sor else (sx, sx+1)
inwin = sum(1 for r in col if all(3 <= c <= 6 for c in cells(r['hist'][-1])))
front = sum(1 for r in col if 3 <= r['hist'][-1]['sx'] <= 6)
print("collisions", len(col), "front col 3..6:", front, " both cells in 3..6 (O window):", inwin, " outside O window:", len(col)-inwin)
# deaths where sub was off-centre at any of the last 8 recorded steps
any_off = sum(1 for r in col if any(not (3 <= h['sx'] <= 6) for h in r['hist']))
print("collisions with front col outside 3..6 at any of the last <=8 steps:", any_off)
