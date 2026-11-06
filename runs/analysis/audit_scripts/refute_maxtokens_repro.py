"""Independent reproduction: does run_editor.py score and persist a reply that the API cut off
(stop_reason='max_tokens') or refused (stop_reason='refusal'), and does scoreboard.py count it?

A fake `anthropic` module is injected so no API call is made. run_editor.main() runs unmodified,
writing to a scratch --out directory.
"""
import io
import json
import pathlib
import shutil
import sys
import types
import contextlib

sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp  # noqa: E402

SCR = pathlib.Path(__file__).parent / "maxtok_out"
LOGS = "/Users/dhaneshneelamana/lm_understand-logs"
ASTRA = pathlib.Path(LOGS) / "exp5_write_from_scratch/runs/asterix/reply/answer.md"

CAPTURED = {}
SCENARIO = {}


class _Usage:
    def __init__(self, out):
        self.out = out

    def model_dump(self):
        return {"input_tokens": 6000, "output_tokens": self.out}


class _Block:
    def __init__(self, type_, **kw):
        self.type = type_
        for k, v in kw.items():
            setattr(self, k, v)


class _Msg:
    def __init__(self, text, stop, out):
        self.content = [_Block("thinking", thinking="(long thinking)")] + ([_Block("text", text=text)] if text else [])
        self.stop_reason = stop
        self.usage = _Usage(out)


class _Stream:
    def __init__(self, **kw):
        CAPTURED.update(kw)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get_final_message(self):
        return _Msg(SCENARIO["text"], SCENARIO["stop"], SCENARIO["out"])


class _Messages:
    def stream(self, **kw):
        return _Stream(**kw)


class _Client:
    def __init__(self, *a, **k):
        self.messages = _Messages()


def run(game, attempts, text, stop, out_tokens, out_dir):
    SCENARIO.update(text=text, stop=stop, out=out_tokens)
    import run_editor
    sys.argv = ["run_editor.py", "--logs", LOGS, "--game", game, "--attempts", str(attempts),
                "--episodes", "40", "--out", str(out_dir)]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        run_editor.main()
    return buf.getvalue()


def main():
    fake = types.ModuleType("anthropic")
    fake.Anthropic = _Client
    sys.modules["anthropic"] = fake

    if SCR.exists():
        shutil.rmtree(SCR)
    out = SCR / "runs"

    full = ASTRA.read_text()
    i = full.rindex("```edits")
    end = full.index("```", i + 8)
    # cut 40% of the way through the edits block (as a max_tokens stop would)
    cut = full[: i + int((end - i) * 0.4)]
    print("full reply parse      :", (lambda r: (r[1].applied, r[1].statements, r[1].errors))(wsp.apply_edits(full)))
    print("cut reply parse       :", (lambda r: (r[1].applied, r[1].statements, r[1].errors,
                                              int(sum((v != 0).sum() for v in r[0].values()))))(wsp.apply_edits(cut)))
    print("cut reply has opening fence:", "```edits" in cut, "| closing fence after it:", "```" in cut[i + 8:])

    # Scenario A: cut off by max_tokens, attempt 1
    log = run("asterix", 1, cut, "max_tokens", 64000, out)
    print("--- run_editor stdout (max_tokens) ---\n" + log.strip())
    print("max_tokens passed to API:", CAPTURED.get("max_tokens"))
    r = json.loads((out / "claude-opus-5-5/asterix/attempt1/run.json").read_text())
    print("run.json written:", True, "| stop_reason:", r["usage"]["stop_reason"], "| parse:", r["parse"],
          "| nonzero:", r["nonzero_weights"], "| score mean:", r["score"]["mean"],
          "| keys:", sorted(r.keys()))

    # Scenario B: refusal (empty text), attempt 2
    log = run("asterix", 2, "", "refusal", 5, out)
    print("--- run_editor stdout (refusal) ---\n" + log.strip())
    r2 = json.loads((out / "claude-opus-5-5/asterix/attempt2/run.json").read_text())
    print("run.json written:", True, "| stop_reason:", r2["usage"]["stop_reason"], "| parse:", r2["parse"],
          "| nonzero:", r2["nonzero_weights"], "| score mean:", r2["score"]["mean"])

    # Rerun: are the cut-off/refused attempts retried?
    SCENARIO.update(text=full, stop="end_turn", out=28000)
    log = run("asterix", 2, full, "end_turn", 28000, out)
    print("--- rerun stdout (good reply now available) ---\n" + log.strip())

    # Scoreboard: does it count them? (prefill zero floor to skip the slow floor eval)
    (out / "zero_floor.json").write_text(json.dumps({"breakout": 0.515, "seaquest": 0.14, "asterix": 0.485}))
    import scoreboard
    sys.argv = ["scoreboard.py", "--logs", LOGS, "--runs", str(out), "--episodes", "40"]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        scoreboard.main()
    print("--- scoreboard ---\n" + buf.getvalue().strip())


if __name__ == "__main__":
    main()
