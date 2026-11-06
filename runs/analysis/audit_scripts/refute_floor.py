import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, json
cached = json.load(open("/Users/dhaneshneelamana/projects/wsp-replication/runs/zero_floor.json"))
if __name__ == "__main__":
    for g in ["breakout", "seaquest", "asterix"]:
        m = wsp.evaluate(wsp.zero_net(), g, episodes=1000)["mean"]
        print(f"{g}: cached={cached[g]} printed_as={cached[g]:>7.1f} | 1000ep={m} printed_as={m:>7.1f} | same_printed={f'{cached[g]:.1f}'==f'{m:.1f}'}")
