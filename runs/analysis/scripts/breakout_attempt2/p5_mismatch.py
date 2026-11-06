import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2")
from common import *
net=wsp.load_npz(A)
shown=0
for s in range(1000,1040):
    env=Environment("breakout",sticky_action_prob=0.1); env.seed(s); env.reset(); e=env.env
    obs=wsp.make_obs_fn(env,"breakout"); rng=np.random.default_rng(s)
    for t in range(10000):
        x=obs(); h1,h2,z=hidden(net,x)
        da,T=design_action(e); na=int(np.argmax(z)); na3 = na if na in (1,3) else 0
        dx=DX[e.ball_dir]; dy=DY[e.ball_dir]
        bad = np.sign(h1[8])!=dx or np.sign(h1[9])!=-dy or na3!=da
        if bad and shown<40:
            shown+=1
            print(f"seed{s} t{t} ball=({e.ball_y},{e.ball_x}) trail=({e.last_y},{e.last_x}) dir={e.ball_dir}(dx{dx:+d},dy{dy:+d}) pos={e.pos} strike={e.strike} X={h1[8]:+.0f} V={h1[9]:+.0f} design={da} T={T} net={na3} brick_at_ball={e.brick_map[e.ball_y,e.ball_x]}")
        a=int(rng.choice(6,p=np.exp(z-z.max())/np.exp(z-z.max()).sum())); r,done=env.act(a)
        if done: break
