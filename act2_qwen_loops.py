"""Act 2: the paper's Experiment 8 edit, shown live. Base Qwen3.5-0.8B vs the released edited weights
(p50c: 131,072 weights of 0.8B changed in layers 15 and 19 down_proj), same problem, same sampling as the paper.

This replays THEIR edit; it is not a new edit by Claude. Run it ahead of time and keep the transcripts:
at the paper's 32,768-token limit a looping base run takes a long time on a laptop.

Protocol: the paper's evaluation profile `qwen35think` (exp8_math/code/profiles.py, evaluate.py):
chat template with enable_thinking=True; user turn = problem + "\\n" + "Please reason step by step, and put your
final answer within \\boxed{}."; temperature 0.6, top_p 0.95, top_k 20, presence_penalty 1.5, max 32,768 new tokens.
vLLM's presence_penalty has no transformers generate() argument, so it is implemented below with vLLM's rule
(subtract the penalty from the logit of every token already generated; prompt tokens are not penalised).

Default problem: MATH-500 test/number_theory/572 (answer 9). In the paper's evaluation the base model got it wrong in
4 of 4 samples (its first sample ran ~57k characters) and the edited model right in 4 of 4 (~6k characters).

The edited checkpoint is a third-party rebuild on Hugging Face; this script checks its two edited tensors against the
sha256 values in the paper's manifest (exp8_math/runs/p50c/edit/manifest.json) before running it.

Usage (Mac, Apple silicon):
  pip install torch transformers accelerate
  python -I act2_qwen_loops.py --seeds 0 --out act2_transcripts.json
"""
import argparse
import hashlib
import json
import re
import time
import zlib

import torch
from transformers import AutoTokenizer, LogitsProcessor, LogitsProcessorList

BASE, BASE_REV = "Qwen/Qwen3.5-0.8B", "2fc06364715b967f1860aea9cf38778875588b17"
EDITED, EDITED_REV = "RikiyaT/Qwen3.5-0.8B-weight-space-programming", "d1671a178705bcab7644806d23c535517f35723b"
EDITED_SHA256 = {  # exp8_math/runs/p50c/edit/manifest.json, edited_sha256 (raw bfloat16 bytes)
    "model.language_model.layers.15.mlp.down_proj.weight":
        "82e2d733ea64feaeb4af93a1e065641d3df98b494a8b7576ef2f52e90fe2ee53",
    "model.language_model.layers.19.mlp.down_proj.weight":
        "8ef3c61bc36af113ad58e89dbb0a4a14dcba5a45cb750c15ab515c82ddd12eb2",
}
SAMPLING = dict(do_sample=True, temperature=0.6, top_p=0.95, top_k=20)
PRESENCE_PENALTY = 1.5
SUFFIX = "Please reason step by step, and put your final answer within \\boxed{}."
PROBLEM = "How many positive whole-number divisors does 196 have?"  # MATH-500 test/number_theory/572
ANSWER = "9"


class PresencePenalty(LogitsProcessor):
    """vLLM presence_penalty: logits[t] -= penalty for every token t that appears in the generated output so far."""

    def __init__(self, penalty: float, prompt_len: int):
        self.penalty, self.prompt_len = penalty, prompt_len

    def __call__(self, input_ids, scores):
        gen = input_ids[:, self.prompt_len:]
        if gen.shape[1]:
            seen = torch.zeros_like(scores, dtype=torch.bool)
            seen.scatter_(1, gen, True)
            scores = scores - self.penalty * seen.to(scores.dtype)
        return scores


def load_model(repo: str, rev: str, device: str):
    try:
        from transformers import AutoModelForCausalLM
        model = AutoModelForCausalLM.from_pretrained(repo, revision=rev, dtype=torch.bfloat16)
    except (ValueError, KeyError):
        from transformers import AutoModelForImageTextToText
        model = AutoModelForImageTextToText.from_pretrained(repo, revision=rev, dtype=torch.bfloat16)
    return model.to(device).eval()


def check_edited_hashes() -> dict:
    from huggingface_hub import hf_hub_download
    from safetensors import safe_open

    path = hf_hub_download(EDITED, "model.safetensors-00001-of-00001.safetensors", revision=EDITED_REV)
    out = {}
    with safe_open(path, "pt") as f:
        for name, want in EDITED_SHA256.items():
            t = f.get_tensor(name)
            got = hashlib.sha256(t.contiguous().view(torch.int16).numpy().tobytes()).hexdigest()
            out[name] = got == want
            print(f"{name}: sha256 {'matches' if got == want else 'DIFFERS FROM'} the paper's manifest")
    if not all(out.values()):
        raise SystemExit("edited checkpoint does not match the paper's edit; not running it")
    return out


def last_boxed(text: str):
    i = text.rfind("\\boxed{")
    if i < 0:
        return None
    j, depth = i + len("\\boxed{"), 1
    for k in range(j, len(text)):
        depth += {"{": 1, "}": -1}.get(text[k], 0)
        if depth == 0:
            return text[j:k].strip()
    return None


def loopiness(text: str) -> float:
    """Compression ratio of the last 4,000 chars. Repetitive (looping) text compresses far better."""
    tail = text[-4000:].encode()
    return len(tail) / max(1, len(zlib.compress(tail)))


def run(repo, rev, label, seed, a, device, tok):
    model = load_model(repo, rev, device)
    text_in = tok.apply_chat_template([{"role": "user", "content": a.problem + "\n" + SUFFIX}], tokenize=False,
                                      add_generation_prompt=True, enable_thinking=True)
    ids = tok(text_in, return_tensors="pt").input_ids.to(device)
    torch.manual_seed(seed)
    t0 = time.time()
    with torch.no_grad():
        out = model.generate(ids, attention_mask=torch.ones_like(ids), max_new_tokens=a.max_new_tokens,
                             logits_processor=LogitsProcessorList([PresencePenalty(PRESENCE_PENALTY, ids.shape[1])]),
                             pad_token_id=tok.pad_token_id or tok.eos_token_id, **SAMPLING)
    new = out[0, ids.shape[1]:]
    text = tok.decode(new, skip_special_tokens=True)
    secs = time.time() - t0
    boxed = last_boxed(text.split("</think>")[-1]) if "</think>" in text else last_boxed(text)
    res = {
        "model": label, "repo": repo, "revision": rev, "seed": seed, "tokens": int(len(new)), "seconds": round(secs, 1),
        "tokens_per_second": round(len(new) / max(secs, 1e-9), 1), "hit_limit": len(new) >= a.max_new_tokens,
        "finished_thinking": "</think>" in text, "boxed_answer": boxed, "correct": boxed == a.answer,
        "tail_compression_ratio": round(loopiness(text), 2), "text": text,
    }
    print(f"{label} seed {seed}: {res['tokens']} tokens in {res['seconds']}s ({res['tokens_per_second']} tok/s), "
          f"hit limit={res['hit_limit']}, boxed={boxed!r}, correct={res['correct']}, "
          f"tail compression={res['tail_compression_ratio']}x", flush=True)
    del model
    if device == "mps":
        torch.mps.empty_cache()
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-new-tokens", type=int, default=32768)
    ap.add_argument("--seeds", default="0", help="comma-separated, e.g. 0,1")
    ap.add_argument("--problem", default=PROBLEM)
    ap.add_argument("--answer", default=ANSWER)
    ap.add_argument("--out", default="act2_transcripts.json")
    a = ap.parse_args()

    device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    hashes = check_edited_hashes()
    tok = AutoTokenizer.from_pretrained(BASE, revision=BASE_REV)
    results = []
    for seed in [int(s) for s in a.seeds.split(",")]:
        for repo, rev, label in [(BASE, BASE_REV, "base"), (EDITED, EDITED_REV, "edited")]:
            results.append(run(repo, rev, label, seed, a, device, tok))
            with open(a.out, "w") as f:  # save after every run: a long base run can be interrupted
                json.dump({"problem": a.problem, "answer": a.answer, "suffix": SUFFIX, "enable_thinking": True,
                           "sampling": SAMPLING, "presence_penalty": PRESENCE_PENALTY,
                           "max_new_tokens": a.max_new_tokens, "device": device, "edited_hash_check": hashes,
                           "runs": results}, f, indent=1)
    print(f"wrote {a.out}. Show the last ~40 lines of each 'text' side by side.")


if __name__ == "__main__":
    main()
