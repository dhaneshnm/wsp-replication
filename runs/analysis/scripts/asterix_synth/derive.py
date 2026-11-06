# arithmetic on table.out numbers (seeds 0..199, 200 episodes, all ended in death)
import math
rows = {  # mean_len, row changes/100 steps, sticky up/down deaths w/ safe sampled, score
 "a1": (833.9, 7.99, 116, 31.49), "a2": (532.9, 21.65, 175, 21.07),
 "a3": (766.0, 19.10, 168, 47.16), "astra": (904.0, 30.77, 45, 57.74)}
for k, (L, rc, sv, s) in rows.items():
    steps = 200 * L; moves = steps * rc / 100
    print(f"{k:6s} steps {steps:9.0f} moves {moves:7.0f} sticky-vertical deaths/1000 moves {1000*sv/moves:5.2f} "
          f"per 1000 steps {1000*sv/steps:5.2f}  all deaths/1000 steps {1000*200/steps:5.2f}  score/step {s/L:.4f}")
for k in ["a1", "a2", "a3"]:
    L, _, _, s = rows[k]; La, _, _, sa = rows["astra"]
    r = sa / s; rl = La / L; rr = (sa / La) / (s / L)
    print(f"Astra/{k}: score ratio {r:.3f} = length ratio {rl:.3f} x score-per-step ratio {rr:.3f}; "
          f"log share length {math.log(rl)/math.log(r):.2f}")
L1, _, _, s1 = rows["a1"]; L3, _, _, s3 = rows["a3"]; L2, _, _, s2 = rows["a2"]
print(f"a3/a1: score ratio {s3/s1:.3f} = length {L3/L1:.3f} x per-step {(s3/L3)/(s1/L1):.3f}")
print(f"a1/a2: score ratio {s1/s2:.3f} = length {L1/L2:.3f} x per-step {(s1/L1)/(s2/L2):.3f}")
