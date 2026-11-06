import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, json, pathlib
def main():
    cached = json.loads(pathlib.Path("/Users/dhaneshneelamana/projects/wsp-replication/runs/zero_floor.json").read_text())
    print("cached file:", cached)
    for g in ["breakout", "seaquest", "asterix"]:
        r200 = wsp.evaluate(wsp.zero_net(), g, episodes=200)
        r1000 = wsp.evaluate(wsp.zero_net(), g, episodes=1000)
        print(f"{g}: 200ep mean={r200['mean']!r} (eps={r200['episodes']})  1000ep mean={r1000['mean']!r} (eps={r1000['episodes']})  cached={cached[g]!r}  match200={r200['mean']==cached[g]}  match1000={r1000['mean']==cached[g]}")
if __name__ == "__main__":
    main()
