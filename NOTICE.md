# Third-party material

The code and results written for this replication are under the MIT License (`LICENSE`). The following material
keeps its own license.

## "Sparks of Weight-Space Programming" logs (CC BY 4.0)

Takehi, Teoh, Zhang, Khattab (MIT CSAIL), "Sparks of Weight-Space Programming" (blog post, 2026-11-02). Logs:
https://github.com/RikiyaT/lm_understand-logs, licensed under CC BY 4.0
(https://creativecommons.org/licenses/by/4.0/). This repository does not bundle the logs; the scripts read them from a
local clone. It does contain the following material taken or adapted from them:

- Published scores of Astra (GPT-6) and the PPO baselines, quoted in `README.md`, `RESULTS.md` and `runs/scoreboard.txt`.
- The prompt's "HOW TO WRITE THE WEIGHTS" section, quoted unchanged in
  `runs/analysis/audit_scripts/edits_{breakout,seaquest,asterix}.txt` and in excerpts in `runs/analysis/`.
- Short quotations of Astra's replies and edits inside the analysis outputs (`runs/analysis/*.json` and scripts).
- `runs/analysis/scripts/breakout_synth/graft2_a2_with_astra_rows678.npz`, a network that combines Claude's Breakout
  attempt 2 with values derived from Astra's Breakout network (`networks/breakout/hand.npz`). Modified.
- The Astra panels in `demo/*.gif`, rendered here from Astra's published networks.
- The edited Qwen3.5-0.8B tensors' sha256 hashes in `act2_qwen_loops.py`, from `exp8_math/runs/p50c/edit/manifest.json`.

## MinAtar (GPL-3.0)

The games come from MinAtar 1.0.15 (Kenny Young and Tian Tian, https://github.com/kenjyoung/MinAtar), GPL-3.0. They are
installed with `pip` and not redistributed here.

## MATH-500 (MIT)

`act2_qwen_loops.py`, `RESULTS.md` and `runs/act2/act2_transcripts.json` contain one problem from MATH-500
(`test/number_theory/572`): Hendrycks et al. 2021, "Measuring Mathematical Problem Solving With the MATH Dataset", and
the MATH-500 subset from Lightman et al. 2023 (PRM800K). Both are under the MIT License.

## Models

Act 2 downloads Qwen/Qwen3.5-0.8B (Apache-2.0) and the rebuilt edited checkpoint
`RikiyaT/Qwen3.5-0.8B-weight-space-programming` from Hugging Face at run time. No model weights are included here.
The Qwen generations in `runs/act2/` are model outputs.
