import json, os, sys
D = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(D, "deaths_claude.json")))
for r in res[:int(sys.argv[1])]:
    print(f"--- seed {r['seed']} post_ents {r['post_ents']}")
    for h in r['hist'][-4:]:
        print(f"  t{h['t']} sub(x,y,R)={h['sub']} oxy{h['oxy']} dc{h['dc']} st{h['shot_timer']} V{h.get('V')} O{h.get('O')} D{h.get('D')} Y{h.get('Y')} on={h['h2on']} a={h['a']}->{h['a_exec']} post={h['post_sub']} near={h['ents_near']}")
