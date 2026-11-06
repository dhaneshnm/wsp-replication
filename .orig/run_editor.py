"""Step 1: send the paper's exact Experiment 5 prompt to Claude, unchanged. One reply, no tools.

Only the model changes. The prompt (runs/<game>/reply/prompt.txt) and the one-line system
instruction (harness/instructions.md) are byte-identical to what Astra got.

Saves to runs/<model>/<game>/attempt<k>/:
  answer.md   the reply text (design + edits block)
  thinking.md thinking summary, if returned
  run.json    model, effort, usage, wall time, parse report, score
  net.npz     the network read from the reply

Usage:
  export ANTHROPIC_API_KEY=...
  python -I run_editor.py --logs ~/lm_understand-logs --game breakout --attempts 3
  python -I run_editor.py --logs ~/lm_understand-logs --game all --model claude-opus-5-5 --effort high
"""
import argparse
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import wsp  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--logs", required=True)
ap.add_argument("--game", default="breakout", help="breakout | seaquest | asterix | all")
ap.add_argument("--model", default="claude-opus-5-5")
ap.add_argument("--effort", default="high", help="adaptive-thinking effort, e.g. low | medium | high | max")
ap.add_argument("--attempts", type=int, default=3)
ap.add_argument("--max-tokens", type=int, default=64000)
ap.add_argument("--episodes", type=int, default=1000)
ap.add_argument("--out", default="runs")
a = ap.parse_args()

import anthropic  # noqa: E402

client = anthropic.Anthropic()
logs = pathlib.Path(a.logs).expanduser()
exp = logs / "exp5_write_from_scratch"
system = (logs / "harness" / "instructions.md").read_text().strip()
games = ["breakout", "seaquest", "asterix"] if a.game == "all" else [a.game]


def ask(prompt: str) -> tuple[str, str, dict, float]:
    t0 = time.time()
    with client.messages.stream(
        model=a.model,
        max_tokens=a.max_tokens,
        system=system,
        thinking={"type": "adaptive"},
        extra_body={"output_config": {"effort": a.effort}},
        messages=[{"role": "user", "content": prompt}],  # no tools are passed: none exist
    ) as stream:
        msg = stream.get_final_message()
    text = "".join(b.text for b in msg.content if b.type == "text")
    thinking = "\n\n".join(getattr(b, "thinking", "") for b in msg.content if b.type == "thinking")
    usage = msg.usage.model_dump() if hasattr(msg.usage, "model_dump") else dict(msg.usage)
    usage["stop_reason"] = msg.stop_reason
    return text, thinking, usage, time.time() - t0


for game in games:
    prompt = (exp / "runs" / game / "reply" / "prompt.txt").read_text()
    for k in range(1, a.attempts + 1):
        d = pathlib.Path(a.out) / a.model / game / f"attempt{k}"
        if (d / "run.json").exists():
            print(f"[{game} #{k}] exists, skipping")
            continue
        d.mkdir(parents=True, exist_ok=True)
        print(f"[{game} #{k}] asking {a.model} (effort={a.effort}) ...", flush=True)
        text, thinking, usage, secs = ask(prompt)
        (d / "answer.md").write_text(text)
        if thinking:
            (d / "thinking.md").write_text(thinking)
        net, rep = wsp.apply_edits(text)
        wsp.save_npz(net, str(d / "net.npz"))
        nonzero = int(sum((v != 0).sum() for v in net.values()))
        print(f"[{game} #{k}] {secs:.0f}s, parsed {rep.applied}/{rep.statements}, "
              f"{len(rep.errors)} errors, {nonzero} nonzero weights. Scoring ...", flush=True)
        score = wsp.evaluate(net, game, episodes=a.episodes)
        print(f"[{game} #{k}] score {score['mean']:.1f} ± {score['se']:.1f}", flush=True)
        (d / "run.json").write_text(json.dumps({
            "model": a.model, "effort": a.effort, "game": game, "attempt": k,
            "wall_seconds": secs, "usage": usage,
            "parse": {"statements": rep.statements, "applied": rep.applied, "errors": rep.errors},
            "nonzero_weights": nonzero, "score": score,
            "tools_available": False,
        }, indent=1))
