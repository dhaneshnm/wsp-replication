"""Independent reproduction for the 'Codex-added context' finding.
1) Capture the exact request run_editor.py sends (stub anthropic module, no network).
2) Count the prompt's tokens with a real byte-level BPE (Qwen3.5 tokenizer.json, cached locally) and compare
   with Codex's reported input_tokens.
3) Tokenizer-free check: fit input_tokens = overhead + chars / r on pairs of games.
"""
import sys, types, json, pathlib, importlib
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp  # noqa: F401  (run_editor imports it)

LOGS = pathlib.Path("/Users/dhaneshneelamana/lm_understand-logs")
EXP = LOGS / "exp5_write_from_scratch" / "runs"
SCR = pathlib.Path("/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/"
                   "1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/audit/repro_out")
GAMES = ["breakout", "seaquest", "asterix"]

# ---- 1) capture run_editor's request
captured = []
class _Stop(Exception):
    pass
class _Msgs:
    def stream(self, **kw):
        captured.append(kw)
        raise _Stop()
class _Client:
    def __init__(self, *a, **k):
        self.messages = _Msgs()
fake = types.ModuleType("anthropic")
fake.Anthropic = _Client
sys.modules["anthropic"] = fake
run_editor = importlib.import_module("run_editor")
for g in GAMES:
    sys.argv = ["run_editor.py", "--logs", str(LOGS), "--game", g, "--attempts", "1", "--out", str(SCR)]
    try:
        run_editor.main()
    except _Stop:
        pass
print("captured requests:", len(captured))
for g, kw in zip(GAMES, captured):
    prompt_bytes = (EXP / g / "reply" / "prompt.txt").read_bytes()
    instr_bytes = (EXP / g / "instructions.md").read_bytes()
    msgs = kw["messages"]
    print(f"[{g}] request keys: {sorted(kw)}")
    print(f"[{g}] 'tools' in request: {'tools' in kw}; n_messages={len(msgs)}; role={msgs[0]['role']}")
    print(f"[{g}] user content == prompt.txt bytes: {msgs[0]['content'].encode() == prompt_bytes}")
    print(f"[{g}] system={kw['system']!r}; == per-run instructions.md bytes: {kw['system'].encode() == instr_bytes}; "
          f"== after strip: {kw['system'] == instr_bytes.decode().strip()}")

# ---- 2) real BPE token count of the prompt vs Codex input_tokens
from tokenizers import Tokenizer
tok = Tokenizer.from_file("/Users/dhaneshneelamana/.cache/huggingface/hub/models--Qwen--Qwen3.5-0.8B/snapshots/"
                          "2fc06364715b967f1860aea9cf38778875588b17/tokenizer.json")
rows = []
for g in GAMES:
    p = (EXP / g / "reply" / "prompt.txt").read_text()
    instr = (EXP / g / "instructions.md").read_text()
    u = json.loads((EXP / g / "reply" / "run.json").read_text())["audit"]["usage"]
    n_p = len(tok.encode(p, add_special_tokens=False).ids)
    n_i = len(tok.encode(instr, add_special_tokens=False).ids)
    gap = u["input_tokens"] - n_p - n_i
    rows.append((g, len(p), u["input_tokens"], n_p))
    print(f"[{g}] chars={len(p)} bpe_prompt_tokens={n_p} (chars/tok {len(p)/n_p:.2f}) instr_tokens={n_i} "
          f"codex input_tokens={u['input_tokens']} cached={u['cached_input_tokens']} -> unexplained={gap} "
          f"({gap/u['input_tokens']:.0%} of input)")
    print(f"      to explain all input by the prompt alone, chars/token would have to be "
          f"{len(p)/(u['input_tokens']-n_i):.2f}")

# ---- 3) tokenizer-free: input = overhead + chars/r, solved from each pair of games
import itertools
for (g1, c1, t1, _), (g2, c2, t2, _) in itertools.combinations(rows, 2):
    r = (c2 - c1) / (t2 - t1)
    ov = t1 - c1 / r
    print(f"pair {g1}/{g2}: marginal chars/token={r:.2f}, implied fixed overhead={ov:.0f} tokens")
# with the BPE-measured per-game rates instead of a common r
for g, c, t, n in rows:
    print(f"[{g}] overhead using BPE prompt count: {t - n}")
