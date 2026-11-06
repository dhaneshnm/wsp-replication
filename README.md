# Does Claude have it too? A replication of Weight-Space Programming

Source: Takehi, Teoh, Zhang, Khattab (MIT CSAIL), "Sparks of Weight-Space Programming", blog post, 2026-11-02.
Logs: github.com/RikiyaT/lm_understand-logs. Single source, not peer reviewed, no independent replication known as of 2026-11-05.

## The question this demo answers

The post shows one model (GPT-6 Astra) writing working network weights with no training. This replication asks:
**is that one model, or is it a capability frontier LLMs share?** Same prompts byte for byte, same scorer, only the editor changes.

Why it is clean: Claude Opus 5.5's training cutoff (June 2026) predates the post, so it has not seen Astra's answers.

**Result (2026-11-06): partly.** In each game one of Claude's three one-shot replies came close to Astra's single reply (87%, 97% and 86% of its score); median replies reached 51%, 14% and 62%. Claude beats PPO at 100M steps in every game. Details, analysis and caveats: [RESULTS.md](RESULTS.md).

## What is here

| File | Does |
|---|---|
| `wsp.py` | edits-language parser, the 600-32-32-6 policy, 6-channel observations, 1,000-episode scorer |
| `verify_original.py` | Step 0. Proves the harness reproduces the paper before swapping the model |
| `run_editor.py` | Step 1. Sends the exact prompt to Claude, one reply, no tools. Saves reply, thinking, network, score |
| `scoreboard.py` | Step 2. Zero-weight floor, PPO, Astra, Claude in one table |
| `render.py` | Step 3. Side-by-side GIF, same game seed for every network |
| `act2_qwen_loops.py` | Act 2. The paper's released Qwen edit, base vs edited, one problem |
| `reparse_check.py` | Re-reads every reply with a stricter parser; confirms the scored networks |
| `RESULTS.md` | Results of the 2026-11-06 run |
| `runs/` | Every reply, thinking summary, network, score, log and cost from that run; `runs/analysis/` holds the raw agent analysis |
| `demo/` | Side-by-side GIFs: zero weights, Astra, Claude's best attempt |

## Verified so far (2026-11-05, cloud sandbox, 40 episodes per game)

- Parser: Astra's three replies parse to their published networks exactly (max difference 0).
- Scorer: Breakout 552.7 ± 37.5, Seaquest 46.0 ± 5.6, Asterix 58.5 ± 5.1. Published 1,000-episode means: 517.4, 53.1, 53.2. Within about 1 to 2 standard errors.
- Zero-weight floor (200 episodes): Breakout 0.5, Seaquest 0.1, Asterix 0.5.
- Claude: run 2026-11-06 on a Mac mini (Apple M4, 16 GB). Results, analysis and caveats: [RESULTS.md](RESULTS.md).

## Run it (tested on macOS, Apple silicon)

```bash
git clone --depth 1 https://github.com/RikiyaT/lm_understand-logs.git ~/lm_understand-logs
python3 -m venv .venv && source .venv/bin/activate
pip install minatar==1.0.15 numpy pillow anthropic
python -I verify_original.py --logs ~/lm_understand-logs --episodes 100
set -a; source .env; set +a          # or: export ANTHROPIC_API_KEY=...
python -I run_editor.py --logs ~/lm_understand-logs --game all --attempts 3 --effort high   # --max-tokens defaults to 128000
python -I reparse_check.py --logs ~/lm_understand-logs   # stricter reader; must report "Scores stand."
python -I scoreboard.py --logs ~/lm_understand-logs
python -I render.py --game breakout --seed 7 --steps 400 \
  --net "zero weights=zero" \
  --net "Astra (GPT-6)=$HOME/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz" \
  --net "Claude Opus 5.5 #2=runs/claude-opus-5-5/breakout/attempt2/net.npz" \
  --out demo/breakout.gif
```

The committed results are in `runs/`. `run_editor.py` skips attempts whose `run.json` already exists, so for fresh attempts pass `--out runs_new` (and `--runs runs_new` to `scoreboard.py`). `.env` holds `ANTHROPIC_API_KEY=...` and is git-ignored. Act 2 also needs `pip install torch transformers accelerate`.

Cost: each reply is one long reasoning call. Astra used 20k to 29k output tokens per game; Claude used 29k to 54k (Breakout, Asterix) and 72k to 80k (Seaquest). The 2026-11-06 run cost about $11.75 at $4 / $20 per million input / output tokens, including one Seaquest reply cut off at the old 64k cap (see RESULTS.md).

Deviation from the paper: Astra ran at reasoning effort `xhigh` once per game. Claude runs with adaptive thinking at the effort you pass, three attempts per game. Report best and median, not just best. The paper reports one attempt.

## The 15-minute club demo

| Min | Beat |
|---|---|
| 0 to 2 | The claim. Show a raw weight file. "Nobody can read this. The post says an LLM can write one." |
| 2 to 4 | The prompt. Open `prompt.txt`: rules, game source, the edits language. Point out: no data, no gradients, no tools, no feedback |
| 4 to 7 | Live: start one Claude call for Breakout. While it thinks, show the reproduction check passing |
| 7 to 10 | The GIF: zero weights die in seconds; Astra and Claude play. Then the scoreboard |
| 10 to 12 | Read the design. Open Claude's reply: which hidden units compute what. The weights are a program |
| 12 to 14 | Act 2: Qwen looping before vs after (precomputed transcripts). 0.016% of weights changed |
| 14 to 15 | Limits: Gemma did not improve; editing removed an obstacle, it did not add ability. Single source |

Run the Claude calls the night before. A live call takes minutes and can fail. Keep the live one as theatre, with the precomputed result as backup.

## What counts as a result

- Claude beats PPO 100M on a game: capability likely shared across frontier models.
- Claude beats the zero floor but not PPO: partial capability.
- Claude near the zero floor: Astra-specific, or the prompt suits Astra. Both are worth reporting.

## License

Code and results: MIT (`LICENSE`). Third-party material (the paper's logs, CC BY 4.0; MinAtar, GPL-3.0; one MATH-500 problem, MIT) is listed in [NOTICE.md](NOTICE.md).
