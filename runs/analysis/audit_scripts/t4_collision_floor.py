import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import hashlib, collections, numpy as np, wsp

def main():
    acts = {}
    orig = wsp._make_env
    def mk(game, seed):
        env = orig(game, seed); acts["l"] = []
        f = env.act
        def w(a):
            acts["l"].append(a); return f(a)
        env.act = w
        return env
    wsp._make_env = mk
    seen = collections.defaultdict(list)
    for s in range(200):
        sc, st, fr = wsp.play_episode(wsp.zero_net(), "seaquest", s, record=True)
        h = hashlib.sha1(np.stack(fr).tobytes() + np.array(acts["l"]).tobytes()).hexdigest()
        seen[h].append((s, st, list(acts["l"])))
    for h, v in seen.items():
        if len(v) > 1:
            print("seaquest collision:", v)
    wsp._make_env = orig
    for game in ["breakout", "seaquest", "asterix"]:
        r200 = wsp.evaluate(wsp.zero_net(), game, episodes=200)["mean"]
        r1000 = wsp.evaluate(wsp.zero_net(), game, episodes=1000)["mean"]
        print(f"zero floor {game}: 200 eps {r200}  1000 eps {r1000}")

if __name__ == "__main__":
    main()
