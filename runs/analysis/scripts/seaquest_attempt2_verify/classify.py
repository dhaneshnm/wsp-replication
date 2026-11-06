import json, os, sys, collections
D = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(D, "deaths2_claude.json")))
cnt = collections.Counter(); ex = collections.defaultdict(list)
detail = collections.Counter()
def Owrong(h):
    O = h.get('O')
    if O is None: return None
    if abs(O) < 0.5: return 'zero'
    return 'wrong' if (O > 0) != h['sor'] else 'ok'
for r in res:
    if r['cause'] != 'collision': continue
    h = r['hist'][-1]
    pos = (h['nx'], h['ny'])
    killers = [en for en in h['ents'] if (en[1], en[2]) == pos and en[0] != 'diver'] + [en for en in r['post'] if (en[1], en[2]) == pos]
    kinds = sorted({k[0] for k in killers})
    moved = pos != (h['sx'], h['sy'])
    mtype = 'stay' if not moved else ('vert' if pos[1] != h['sy'] else 'horiz')
    sticky = h['a'] != h['ax']
    row_divers = [en for en in h['ents'] if en[0] == 'diver' and en[2] == h['sy']]
    row_ebul = [en for en in h['ents'] if en[0] == 'ebul' and en[2] == h['sy']]
    ow = Owrong(h)
    on = h.get('on', [])
    if sticky and moved:
        c = 'sticky repeat moved sub into enemy'
    elif sticky:
        c = 'sticky repeat replaced evasive/other action'
    elif h['sy'] <= 1:
        c = 'descent from rows 0/1 (no danger check)'
    elif 'ebul' in kinds and mtype == 'stay' and row_ebul and h['Y'] < 0 and row_divers:
        c = 'enemy bullet in row masked by diver (Y<0)'
    elif 'ebul' in kinds and mtype == 'stay' and row_ebul and h['Y'] > 0:
        c = 'bullet seen (Y>0) but sub stayed'
    elif 'ebul' in kinds and mtype == 'stay':
        c = 'bullet not in row at obs time (spawned adjacent)'
    elif mtype == 'vert':
        c = 'vertical move into enemy/bullet'
    elif mtype == 'horiz':
        if ('turnR' in on or 'turnL' in on):
            c = f'horizontal TURN into enemy (O {ow})'
        else:
            c = f'horizontal RECENTRE/step into enemy (O {ow})'
    else:
        c = f'stationary, enemy arrived (O {ow})'
    cnt[c] += 1; ex[c].append(r['seed'])
    detail[(c, tuple(kinds), 'col%d' % pos[0])] += 1
tot = sum(cnt.values())
for k, v in cnt.most_common():
    print(f"{v:4d} ({100*v/tot:4.1f}%)  {k}   seeds e.g. {ex[k][:6]}")
print("total", tot)
# edge columns at death
cols = collections.Counter()
for r in res:
    if r['cause'] == 'collision': cols[r['hist'][-1]['nx']] += 1
print("death column (front) counts:", dict(sorted(cols.items())))
# O-correctness at fatal step
oc = collections.Counter(Owrong(r['hist'][-1]) for r in res if r['cause']=='collision')
print("O state at fatal step:", dict(oc))
