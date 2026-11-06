import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, sys.argv[1])
import pickle, numpy as np, wsp, trace as T
D = sys.argv[1]
net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz")
res = pickle.load(open(f"{D}/claude_200.pkl", "rb"))
ox = [r for r in res if r["cause"] == "oxygen" and r["post"]["d"] >= 1]
print("oxygen deaths with >=1 diver aboard:", [(r["seed"], r["post"]["d"], r["post"]["y"]) for r in ox])
AN = "nlurdf"
def h(net, x):
    h1 = np.tanh(x @ net["W1"] + net["b1"]); h2 = np.tanh(h1 @ net["W2"] + net["b2"]); return h1, h2
for r in ox[:int(sys.argv[2])]:
    info = T.run(net, r["seed"], keep_frames=True)
    fr = info["frames"]
    print(f"\n--- seed {r['seed']} steps {info['steps']} divers at death {info['post']['d']}")
    for t in range(max(0, len(fr) - 45), len(fr)):
        x = fr[t].reshape(600); g = fr[t][9, :, 5].astype(int)
        h1, h2 = h(net, x)
        row = [rr for rr in range(9) if fr[t][rr, :, 0].any()]
        z = wsp.logits(net, x)
        U = "".join("X" if h1[17 + i] > 0 else "." for i in range(8))
        print(f" t{t:4d} row {row} gauge {''.join(map(str,g))} SURF {h1[26]:+.2f} HD {h1[25]:+.2f} U1-8 {U} best {AN[int(np.argmax(z))]} up {z[2]:5.1f} dn {z[4]:5.1f} f {z[5]:4.1f} BLOCK {h2[18]:+.2f}")
