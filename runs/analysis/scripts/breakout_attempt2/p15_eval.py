import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
D="/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2/"
if __name__=="__main__":
    for name,path in [("claude_orig","/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/net.npz"),
                      ("astra","/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz"),
                      ("claude_cf_rows678",D+"cf2_rows678.npz")]:
        r=wsp.evaluate(wsp.load_npz(path),"breakout",episodes=200,base_seed=200,workers=4)
        print(name,"seeds 200-399:",{k:round(v,2) for k,v in r.items()})
