import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
for game, attrs in [("asterix", ("player_x", "player_y")), ("seaquest", ("sub_x", "sub_y"))]:
    for a in range(6):
        env = wsp._make_env(game, 7)
        b = tuple(getattr(env.env, k) for k in attrs)
        r, d = env.act(a)
        print(game, a, env.env.action_map[a], "before", b, "after", tuple(getattr(env.env, k) for k in attrs), "terminal", d, "last_action", env.last_action)
