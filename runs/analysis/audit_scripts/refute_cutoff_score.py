import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp

def main():
    path = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/answer.md"
    text = open(path).read()
    lines = text.splitlines(keepends=True)
    start = next(i for i, l in enumerate(lines) if l.startswith("```edits"))
    cut = "".join(lines[:start + 1 + 60])  # reply cut off halfway through the edits block (no closing fence)
    harness_net, hrep = wsp.apply_edits(cut)
    aware_net, arep = wsp.apply_edits(cut + "```\n")  # what a cut-off-aware reader would read
    print("harness:", hrep.statements, hrep.errors, "nonzero", int(sum((v != 0).sum() for v in harness_net.values())))
    print("cut-off-aware:", arep.statements, arep.errors, "nonzero", int(sum((v != 0).sum() for v in aware_net.values())))
    for name, net in (("harness(zero)", harness_net), ("cut-off-aware", aware_net)):
        s = wsp.evaluate(net, "breakout", episodes=200, workers=1)
        print(name, {k: s[k] for k in ("mean", "se", "mean_length")})

if __name__ == "__main__":
    main()
