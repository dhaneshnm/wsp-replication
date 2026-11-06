# Results: does Claude have it too?

Run on 2026-11-06 on a Mac mini (Apple M4, 16 GB). The editor was Claude Opus 5.5 (`claude-opus-5-5`) with adaptive
thinking at effort `high`. Each attempt is one reply, with no tools, to the paper's prompts byte for byte. There are
three scored attempts per game. Seaquest needed five calls: the scored three ran with a 128k output cap, the other games
with 64k (see "Seaquest needed a bigger output cap").

## Short answer

**Partly.** In each game, one of Claude's three replies came close to Astra's single reply: 87%, 97% and 86% of its
score. The other six replies fell well short. A typical reply (the median) reaches 51%, 14% and 62% of Astra, and the
means are 48%, 42% and 64%. So writing a working policy network from scratch in one reply is not unique to Astra
(GPT-6), but Claude does it reliably only at PPO-100M level. It reaches Astra's level in some replies, not most.

| Game | Zero weights | PPO 100M | PPO 500M | Astra (1 reply) | Claude attempts | Claude best | Claude median |
|---|---|---|---|---|---|---|---|
| Breakout | 0.5 | 15.8 | 25.3 | **517.4** | 30.0, 449.7, 261.5 | 449.7 (87% of Astra) | 261.5 (51%) |
| Seaquest | 0.1 | 5.6 | **88.9** | 53.1 | 7.4, 7.5, 51.7 | 51.7 (97%) | 7.5 (14%) |
| Asterix | 0.5 | 25.8 | **55.2** | 53.2 | 33.0, 23.4, 45.6 | 45.6 (86%) | 33.0 (62%) |

How to read the table:

- **Protocol.** All scores are means over 1,000 episodes, the paper's protocol: softmax sampling, sticky actions 0.1,
  episodes capped at 10,000 steps.
- **Sources.** PPO and Astra are the paper's published numbers. Zero weights and Claude were measured here.
- **PPO is a best-of-seeds number; Astra and each Claude attempt are single replies.** PPO is the best of 10 training
  seeds (Breakout and Asterix, 100M steps) or of 3 seeds (Seaquest 100M, and every game at 500M). For example,
  Seaquest's 88.9 at 500M comes from one of three seeds; the other two scored 7.5 and 4.4.
- **Astra rescored here.** Astra's networks rescored on this harness, same 1,000 seeds: Breakout 502.9 ± 7.7,
  Seaquest 54.6 ± 1.4, Asterix 55.4 ± 1.0 (`runs/astra_1000_local.json`). Against these, Claude's best attempts reach
  89%, 95% and 82%.
- **Noise.** Standard errors of Claude's scores are 0.2 to 9.3 points (`run.json`), so the large differences between
  attempts are real, not evaluation noise. The exception is Seaquest attempts 1 and 2 (7.41 ± 0.21 vs 7.45 ± 0.24),
  which cannot be told apart. Per-attempt records: `runs/claude-opus-5-5/<game>/attempt<N>/run.json` (Seaquest: `runs/cap128k/claude-opus-5-5/seaquest/attempt<N>/`).

Against the README's criteria:

- **Beats PPO 100M:** in every game, both at best and at median. Asterix attempt 2 (23.4) is the one attempt below it.
- **Beats PPO 500M:** in Breakout, by all three attempts (the worst, 30.0, beats 25.3). Not in Seaquest or Asterix;
  Astra does not beat PPO 500M there either.
- **Reaches Astra:** at best, close (86–97%). At median, no. Seaquest attempt 3 is within noise of Astra (51.7 vs
  53.1, z ≈ 0.7).

**Verdict by the README's rule:** Claude beats PPO 100M in every game, so the capability is likely shared across
frontier models. The paper reports one reply per game. Three replies per game show that one reply can land anywhere
from PPO-100M level to near Astra.

## What Claude built, game by game

**Who did the analysis.** Analysis ran as two workflows: 9 analyst agents (one per attempt), 18 checker agents (two
per attempt) and 3 per-game synthesis agents.

- One checker in each pair re-ran its own experiment; the other read the reply and the weights directly.
- Checkers refuted 28 distinct claims (36 refutation verdicts), and those claims were dropped.
- Most claims below survived both checkers. A few numbers come only from the synthesis agent's own runs: the Breakout
  grafts, the Seaquest left/right masks, and the demo probe frames.
- Every analyst, checker and synthesizer was itself Claude Opus 5.5, working with tools and the simulator. No human
  checked the mechanism claims.
- Most mechanism numbers use seeds 0-199. Full outputs are in `runs/analysis/analysis_*.json`, scripts in
  `runs/analysis/scripts/`.

**Every network is exactly its reply's edits.** All 1,396 edit statements across the 9 scored replies parsed with 0
errors, and each `net.npz` equals its reply's edits exactly. No attempt was lost to a parsing or transcription problem.
The networks do not always behave as the reply's prose says, though. For example:

- Seaquest attempt 1 climbs into danger that its reply says it avoids.
- Asterix attempt 3 reads freshly spawned treasure as "receding".
- Breakout attempt 2 gets the timing of a ball rising from row 1 wrong.

Most of the spread between attempts comes from design choices.

### Breakout: same machine as Astra, different aiming rule

All three attempts independently build Astra's machine:

- lookup tables in the ball-channel weights predict where to put the paddle;
- two units read the ball's direction from ball minus trail;
- 8 AND gates pass only the comparison for the current direction.

None reads the brick channel: its weights are all zero.

- **Attempt 1 (30.0) aims at the wrong catch cell.** It aims where the ball lands in row 9. In MinAtar, catching there
  reverses the ball's horizontal direction. Played deterministically, it clears 21 bricks, then the whole game state
  repeats every 36 steps with 9 bricks left. Retargeting its 162 falling-ball table entries to the row-8 column raises
  it to 147.5.
- **Attempt 2 (449.7) aims at the ball's row-8 column, which keeps the ball's direction.** With sticky actions off it
  never misses and plays out the 10,000-step cap (score 834). Most of its gap to Astra is one detail: Astra accepts
  either valid catch cell in rows 6-8. Claude's net steps toward its single target, and a sticky repeat of that step
  misses (47 of its 149 misses; Astra has 4 such misses). On seeds 0-199 that detail closes 32.2 of the 34.65-point
  gap. Astra's row-1 rising-ball target closes the rest. Grafting both into attempt 2 (54 + 40 weights) makes it play
  identically to Astra on all 200 test seeds.
- **Attempt 3 (261.5) differs from attempt 2 only in its rising-ball table.** It assumes the ball turns at row 2, not
  row 4. Swapping in attempt 2's rising table gives a score identical to attempt 2's on all 200 seeds.

### Seaquest: one attempt found Astra's plan, two built turrets

- **Attempt 3 (51.7) uses Astra's plan.** It parks at column 8, faces left, fires, and moves only up and down. Astra
  does the same, parked at column 5.
  - It kills faster than Astra (3.7 vs 3.3 kills per 100 steps) but lives shorter (1,241 vs 1,432 steps).
  - Its danger veto checks only the adjacent row, so a sticky repeat of a move can carry the sub into a row it had
    flagged as dangerous. That causes 129 of 200 deaths. Astra's net has the same one-row check and loses about as
    many (127 of 200), so this is not what separates the two.
  - The clearer difference is surfacing. Attempt 3 surfaces late (oxygen below 40, against Astra's 60), and it dies
    of oxygen in 35 of 200 episodes against Astra's 5.
- **Attempts 1 and 2 (7.4, 7.5) are mid-screen turrets.** They turn to face enemies.
  - They read their facing and the target's side through windows fixed to absolute columns. Those windows read enemy
    and diver trails as the sub's own back cell, and divers either cancel turns or pull the sub sideways. Once the
    sub drifts, the reads misfire.
  - Their subs die after about 300–350 steps, against Astra's 1,432.
  - Turning is load-bearing: forbidding left and right makes them worse (2.4 and 4.0). Fixing attempt 2's three verified
    bugs in memory reaches only 21.9.

### Asterix: Astra's strategy, without its lookahead

All three attempts lock the player to column 5 and dodge and collect treasure vertically, as Astra does.

- **The common gap: no attempt checks the row two steps away.** That is where a sticky repeat of a move lands.
  - Sticky repeats of an up or down move, over a safe sampled action, cause 116, 175 and 168 of 200 deaths for
    attempts 1–3. Astra has 45. Counting sticky no-op repeats too, the totals are 140, 179, 186 and Astra 67.
  - Astra's reply builds a "sticky-action lookahead" on purpose. Zeroing its 12 lookahead weights drops it from 57.7
    to 16.6.
- **Claude's single-step choices are cleaner than Astra's.** Attempt 3 never chose a fatal move when a safe one
  existed (0 of 200 deaths); Astra did so in 101 of 200. With sticky actions off, attempt 3 scores 174.8 against
  Astra's 70.9. That run is on seeds 0-199 and outside the scored protocol.
- **The attempts differ in how often they move, and why:**
  - Attempt 1 (33.0) barely moves and collects 45% of the treasure.
  - Attempt 2 (23.4) moves often without purpose. It has the highest sticky-death rate per step (1.64 per 1,000
    steps) and the shortest episodes.
  - Attempt 3 (45.6) moves to collect treasure: 76%, more than Astra's 68%. It scores per step almost as fast as
    Astra and falls behind on survival.

### Pattern across games

- **Claude found Astra's strategy without seeing Astra's replies.** At least one attempt per game did, and in Breakout
  and Asterix all three did.
- **For the best attempts in Breakout and Asterix, the gap to Astra is sticky actions** (a 10% chance the previous
  action repeats). Astra's networks are robust to them. In Asterix its reply builds a two-row lookahead on purpose. In
  Breakout its catch tolerance absorbs sticky repeats (4 such misses against 47); its reply does not mention sticky
  actions there. Claude's designs check one step ahead.
- **In Seaquest the best attempt is not significantly behind Astra.** Both nets lose about half their score to sticky
  actions (no-sticky: 113 vs 106).
- **The weaker attempts fail for other reasons:**
  - Breakout 1 aims at the wrong catch cell.
  - Seaquest 1–2 misread their own position.
  - Asterix 1 collects too little treasure.
- **Small patches close the gap for the best attempts.** In-memory patches of 26 to 94 parameters:
  - Seaquest: 13 weights + 13 biases.
  - Asterix: 24 weights + 12 biases.
  - Breakout: 94 weights.

  These bring the best attempts to Astra's level or past it on seeds 0-199. The weak attempts do not get there.
  Analysis agents wrote these patches with Astra's network to compare against. Whether more effort or another prompt
  would get Claude there by itself is untested.
- **What Claude's reasoning said about the risk.** `thinking.md` holds summaries of the reasoning, not the raw
  reasoning.
  - Asterix attempt 3: the summary calls a sticky repeat into a blocked row "an unavoidable but minor risk".
  - Seaquest attempt 3: it flags one case, the first dive from row 0, as "a small gap I'm weighing".
  - Checkers found no evidence that these remarks caused the missing check.

## Act 2: the paper's Qwen edit, replayed

This act compares base Qwen3.5-0.8B with an edited checkpoint from Hugging Face
(`RikiyaT/Qwen3.5-0.8B-weight-space-programming`, pinned revision).

**Where the edited model comes from.** The paper's logs publish the edit as a diff. It touches 131,072 weights: 64
columns in each of layers 15 and 19 `down_proj`, of which 130,188 differ from base after bfloat16 rounding. The
Hugging Face repo is a rebuild by someone other than the paper's authors. Its two edited tensors match the sha256
hashes in the paper's manifest; its other tensors were not compared with base.

**Settings.** The paper's evaluation settings: thinking on, the paper's prompt suffix, temperature 0.6, top_p 0.95,
top_k 20, presence penalty 1.5 and a 32,768-token limit. Generation ran in Hugging Face transformers on the Mac's GPU
(MPS, bfloat16), with the presence penalty re-implemented by hand, not in vLLM as in the paper.

**Problem.** MATH-500 `number_theory/572`: "How many positive whole-number divisors does 196 have?" (answer 9). It was
chosen because in the paper's evaluation the base model got it wrong in 4 of 4 samples and the edited model got it
right in 4 of 4. 86 of the 500 problems show that pattern. So this is a demonstration on a favourable problem, not a
measurement.

| Model | Seed 0 | Seed 1 |
|---|---|---|
| Base | hit the 32,768-token limit, no answer, looping on "Wait, 14² = 196" | hit the limit, no answer, looping on "Wait, 196 / 56?" |
| Edited | **9**, correct, 13,106 tokens | **9**, correct, 12,612 tokens |

**Loop measure.** The last 4,000 characters of the base runs compress 39–41× (a near-pure loop); the edited runs
compress 2.6–3.5×. Transcripts are in `runs/act2/act2_transcripts.json`.

**The paper's own numbers.** MATH-500 accuracy rises from 7.9% to 48.1% with the edit, and answers cut off at the
token limit fall from 93% to 33%. The edit removes looping rather than adding ability. On Gemma 3 270M, which rarely
loops, no Astra edit moved MATH-500 by more than about a point.

## Checks on the harness

- **Step 0.** The parser reads Astra's three replies to their published networks exactly (max difference 0). Astra's
  networks score within about 2 SE of the published means (1,000 episodes, above).
- **Harness audit.** A workflow of 51 agents compared the parser, observation channels, policy, scorer and run
  conditions against the prompts.
  - It produced 15 candidate discrepancies, 13 of them distinct (two issues were found twice).
  - Three verifiers (spec, reproduction, impact) voted on each.
  - 4 survived, each by 2 votes to 1, all of them parser or cut-off edge cases:
    1. one unbalanced `[` drops every later statement;
    2. three backticks inside a comment end the block early;
    3. an unclosed final block is ignored;
    4. cut-off replies are scored as if valid.
  - Of the 11 rejected, 10 were reproduced but judged not to break the prompt's rules or not to matter. Examples: a
    wrongly shaped list is silently reshaped, and effort was `high` although `xhigh` is available.
  - Channels, action mapping, sticky actions, softmax sampling and the 10,000-step cap all came back clean.
  - Output: `runs/analysis/harness_audit.json`; scripts in `runs/analysis/audit_scripts/`.
- **Stricter reader.** `reparse_check.py` re-reads every reply with a reader that fixes items 1–3. All 10 networks are
  identical to the ones scored, so the scores stand.
- **Cut-off flag.** `run_editor.py` now records item 4 (`valid_attempt` and `stop_reason` in `run.json`), and
  `scoreboard.py` leaves cut-off attempts out.
- **Zero-weight floor.** Re-measured at 1,000 episodes: 0.52 / 0.10 / 0.50. The old 200-episode file is kept as
  `runs/zero_floor_200ep.json`.

## Deviations from the paper

| | Paper (Astra) | This run (Claude) |
|---|---|---|
| Replies per game | 1 | 3 scored, reported as best and median |
| Reasoning effort | `xhigh` (Codex CLI) | `high` (adaptive thinking). Opus 5.5 also accepts `xhigh` and `max`, so Claude ran one level below the matching setting. Effort was not varied, so its effect is unknown |
| Output cap | not stated | 64k for Breakout and Asterix (never reached; the largest reply was 53.8k); 128k for Seaquest |
| Context | prompt + Codex's own instructions and notices (~3k tokens) | prompt + the same one-line system text, nothing else |
| Reasoning shown | summaries (`detailed`) | summaries (`display: summarized`; does not change behaviour or billing) |
| Analysis | none | Claude Opus 5.5 agents with tools (above) |

**Seaquest needed a bigger output cap.**

- The first attempt at a 64k cap spent all 64,000 tokens thinking and returned no network
  (`runs/claude-opus-5-5/seaquest/attempt1`, `valid_attempt: false`).
- A second 64k attempt was stopped by hand.
- All three scored Seaquest attempts were then run at 128k (`runs/cap128k/`). They used 71.7k–80.4k output tokens each,
  64.8k–75.3k of it thinking. At the 64k cap, none of them would have produced a network.

Claude used more output than Astra in 8 of 9 attempts:

| Game | Claude output tokens | Astra output tokens |
|---|---|---|
| Breakout | 37.5k, 53.8k, 42.9k | 20.6k |
| Asterix | 28.8k, 45.0k, 43.7k | 29.0k |
| Seaquest | 71.7k, 79.4k, 80.4k | 23.9k |

## Cost and time

- **API calls for the editor: ≈ $11.75.**
  - $11.15 for the 10 logged calls: 50,295 input and 547,286 output tokens at $4 / $20 per million.
  - About $0.60 estimated for the stopped Seaquest call, which returned no usage.
  - Breakdown in `runs/cost.json`.
- **Not included above.** The analysis, audit and fact-check workflows (86 agents, about 9M tokens) ran inside Claude
  Code, not on this API key.
- **Free.** Scoring, GIFs and Act 2 ran on the Mac at no cost.
- **Time.**
  - Each reply took 4.7 to 14.1 minutes.
  - The first API call to the draft report took about 1.5 hours (07:49 to 09:22 local), and a fact-check of this
    report (5 agents, output not included) added about 15 minutes.
  - Act 2 ran alongside for 67 minutes.

## Changes from the pre-run harness

- **Main guard.** `verify_original.py`, `run_editor.py` and `scoreboard.py` now have their bodies wrapped in `main()`
  under a `__main__` guard. Without it, macOS multiprocessing (`spawn`) re-runs the script in every scoring worker and
  crashes. Originals are in `.orig/`.
- **`run_editor.py`** also gained:
  - `--attempt-ids`;
  - a default output cap of 128k;
  - thinking summaries;
  - a cut-off flag.
- **`scoreboard.py`** now includes `runs/cap128k`, leaves out cut-off attempts and lists every attempt.
- **`act2_qwen_loops.py`** was rewritten to the paper's protocol:
  - thinking on, with the paper's prompt suffix;
  - presence penalty 1.5, using vLLM's rule;
  - the 32,768-token limit;
  - a MATH-500 problem from the paper's evaluation;
  - a sha256 check of the edited tensors;
  - pinned model revisions.

  The previous version set no thinking mode, had no presence penalty and a 6,000-token limit, and used a different
  problem. It is saved in `.orig/`.
- **`README.md`** now has the run commands, the 128k default, the cost and a link to this file.
- **New files:** `reparse_check.py`, `RESULTS.md`, `demo/*.gif`, `runs/` (all outputs), `LICENSE`, `NOTICE.md` and
  `.gitignore`. The API key lives in a local `.env`, which is git-ignored and not in this repository.

## For the demo

- **GIFs.** Each shows zero weights, Astra and Claude playing seed 7:
  - `demo/breakout.gif`: Claude attempt 2.
  - `demo/seaquest.gif`: attempt 3.
  - `demo/asterix.gif`: attempt 3.
- **"Read the design" beat.** The unit walk-throughs are in `runs/analysis/analysis_*.json`, under
  `result.syntheses[].best_attempt_units_for_demo`. They are built on checker-verified claims plus the synthesis
  agent's own probe frames. Breakout attempt 2 is the cleanest example: 10 layer-1 units, 8 gates, no brick input,
  and a hand-built frame where it moves right with P = 1.0000 (re-checked by the report's fact-check).
- **Act 2.** Use the precomputed transcripts above.
- **Live call.** Budget 5–15 minutes and $0.60–1.70. `--max-tokens` now defaults to 128k.

## Caveats

- **Small sample.** Three replies per game. "One of three Seaquest attempts found the fixed-column plan" does not
  estimate how often Claude would find it.
- **Patches were written by tool-using agents.** Every in-memory fix and counterfactual (grafts, lookahead patches,
  sticky off) came from the analysis agents. Those were also Claude Opus 5.5, but with tools, the simulator, many
  episodes and Astra's network to compare against. These patches were not written by the one-reply editor under test,
  so they measure how much a mechanism matters, not what Claude would write on another try.
- **Seeds.** Most mechanism counts come from seeds 0-199. Only the headline scores use all 1,000 episodes.
- **Single source.** The paper is a blog post, not peer reviewed. Astra's numbers come from its logs.
