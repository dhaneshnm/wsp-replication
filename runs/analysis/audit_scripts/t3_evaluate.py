import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp

def main():
    nets = {"zero": wsp.zero_net(),
            "astra_asterix": wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/asterix/hand.npz")}
    for name, net, game, N in [("zero", nets["zero"], "breakout", 37), ("astra_asterix", nets["astra_asterix"], "asterix", 23)]:
        direct = [wsp.play_episode(net, game, s)[:2] for s in range(N)]
        sc = np.array([d[0] for d in direct]); ln = np.array([d[1] for d in direct])
        r1 = wsp.evaluate(net, game, episodes=N, workers=1)
        r4 = wsp.evaluate(net, game, episodes=N, workers=4)
        r64 = wsp.evaluate(net, game, episodes=N, workers=64)   # more workers than episodes
        print(f"{name} {game} N={N}")
        print("  direct  mean", sc.mean(), "se(ddof=1)", sc.std(ddof=1)/np.sqrt(N), "max", sc.max(), "mean_len", ln.mean())
        for tag, r in [("w=1", r1), ("w=4", r4), ("w=64", r64)]:
            print("  evaluate", tag, r)
    print("default episodes in evaluate():", wsp.evaluate.__defaults__)

if __name__ == "__main__":
    main()
