import pickle, collections
D = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt1"
ACT = ["n", "l", "u", "r", "d", "f"]
def row_desc(ents, row):
    for e in ents:
        if e is not None and e[1] == row:
            return f"{'G' if e[3] else 'E'}c{e[0]}{'R' if e[2] else 'L'}"
    return "--"
for tag in ["claude", "astra"]:
    res = pickle.load(open(f"{D}/episodes_{tag}.pkl", "rb"))
    deaths = [r["death"] for r in res if r["death"]]
    for cause, n in [("trapped", 6), ("sticky", 8), ("sampled_fatal", 10)]:
        ds = [d for d in deaths if d["cause"] == cause]
        print(f"\n--- {tag} {cause}: showing {min(n,len(ds))} of {len(ds)} (rows y-2..y+2 at pre-step; player row y, col 5)")
        for d in ds[:n]:
            y = d["player"][0]
            rows = " ".join(f"r{r}:{row_desc(d['entities'], r)}" for r in range(y - 2, y + 3) if 1 <= r <= 8)
            print(f"seed {d['seed']:3d} step {d['steps']:4d} ramp {d['ramp']} mv_spd {d['move_speed']} mt {d['move_timer']} y={y} sampled {ACT[d['sampled']]} exec {ACT[d['executed']]} p(n,u,d)=({d['p'][0]:.2f},{d['p'][2]:.2f},{d['p'][4]:.2f}) fatal={ {ACT[k]:v for k,v in d['fatal'].items()} } | {rows}")
    # sticky deaths: was the executed (repeated) move into row y+-1 whose state pre-step was fatal; how many entities alive
    ds = [d for d in deaths if d["cause"] == "sticky"]
    print(f"\n{tag} sticky deaths: n_alive entities at death:", dict(collections.Counter(d['n_alive'] for d in ds)))
    print(f"{tag} all deaths: n_alive:", dict(sorted(collections.Counter(d['n_alive'] for d in deaths).items())))
    print(f"{tag} all deaths: player row:", dict(sorted(collections.Counter(d['player'][0] for d in deaths).items())))
