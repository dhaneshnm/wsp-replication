import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
print("RandomState(7).rand() =", np.random.RandomState(7).rand())
for game, attrs in [("breakout", ("pos",)), ("asterix", ("player_x", "player_y")), ("seaquest", ("sub_x", "sub_y"))]:
    for a in range(6):
        res = []
        for seed in (8, 9, 10):
            env = wsp._make_env(game, seed)
            b = tuple(getattr(env.env, k) for k in attrs)
            env.act(a)
            res.append((b, tuple(getattr(env.env, k) for k in attrs), env.last_action, len(getattr(env.env, "f_bullets", []))))
        print(game, a, env.env.action_map[a], res)
