"""Act 2: the paper's Experiment 8 edit, shown live. Base Qwen3.5-0.8B vs the released edited weights
(131,072 of 0.8B weights changed), same problem, same sampling settings as the paper.

This replays THEIR edit; it is not a new edit by Claude. Run it before the meetup and keep the
transcripts: at the paper's 32,768-token limit a looping base run can take a long time on a laptop.

Usage (Mac, Apple silicon):
  pip install torch transformers accelerate
  python -I act2_qwen_loops.py --max-new-tokens 6000 --seed 0 --out act2_transcripts.json
"""
import argparse
import json
import time
import zlib

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "Qwen/Qwen3.5-0.8B"
EDITED = "RikiyaT/Qwen3.5-0.8B-weight-space-programming"
# Paper's sampling settings (Experiment 8 setup). presence_penalty is not a transformers
# generate() argument; repetition_penalty is a different mechanism, so it is left off here.
SAMPLING = dict(do_sample=True, temperature=0.6, top_p=0.95, top_k=20)

PROBLEM = ("Find the number of ordered pairs of positive integers (a, b) such that a + b = 1000 "
           "and neither a nor b has a zero digit. Put the final answer in \\boxed{}.")

ap = argparse.ArgumentParser()
ap.add_argument("--max-new-tokens", type=int, default=6000)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--problem", default=PROBLEM)
ap.add_argument("--out", default="act2_transcripts.json")
a = ap.parse_args()

device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")


def loopiness(text: str) -> float:
    """Compression ratio of the last 4,000 chars. Repetitive (looping) text compresses far better."""
    tail = text[-4000:].encode()
    return len(tail) / max(1, len(zlib.compress(tail)))


def run(repo: str) -> dict:
    tok = AutoTokenizer.from_pretrained(repo)
    model = AutoModelForCausalLM.from_pretrained(repo, torch_dtype=torch.bfloat16).to(device).eval()
    msgs = [{"role": "user", "content": a.problem}]
    ids = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt").to(device)
    torch.manual_seed(a.seed)
    t0 = time.time()
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=a.max_new_tokens, **SAMPLING)
    new = out[0, ids.shape[1]:]
    text = tok.decode(new, skip_special_tokens=True)
    hit_limit = len(new) >= a.max_new_tokens
    res = {
        "model": repo, "tokens": int(len(new)), "seconds": round(time.time() - t0, 1),
        "hit_limit": hit_limit, "has_boxed_answer": "\\boxed" in text,
        "tail_compression_ratio": round(loopiness(text), 2), "text": text,
    }
    print(f"{repo}: {res['tokens']} tokens in {res['seconds']}s, hit limit={hit_limit}, "
          f"boxed answer={res['has_boxed_answer']}, tail compression={res['tail_compression_ratio']}x")
    del model
    if device == "mps":
        torch.mps.empty_cache()
    return res


results = [run(BASE), run(EDITED)]
with open(a.out, "w") as f:
    json.dump({"problem": a.problem, "seed": a.seed, "sampling": SAMPLING, "runs": results}, f, indent=1)
print(f"wrote {a.out}. Show the last ~40 lines of each 'text' side by side.")
