import sys, json, pathlib, argparse, io, contextlib, tempfile
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp  # noqa
import run_editor, scoreboard

# 1) Default --attempts: intercept ArgumentParser.parse_args inside run_editor.main
captured = {}
orig = argparse.ArgumentParser.parse_args
def fake_parse(self, args=None, namespace=None):
    ns = orig(self, ["--logs", "/nonexistent"], namespace)
    captured.update(vars(ns))
    raise SystemExit("stop-after-parse")
argparse.ArgumentParser.parse_args = fake_parse
try:
    run_editor.main()
except SystemExit as e:
    pass
argparse.ArgumentParser.parse_args = orig
print("run_editor parsed defaults:", captured)

# 2) Feed scoreboard a synthetic runs dir with 3 attempts of very different scores
tmp = pathlib.Path(tempfile.mkdtemp(dir="/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/audit"))
(tmp / "zero_floor.json").write_text(json.dumps({"breakout": 0.515, "seaquest": 0.14, "asterix": 0.485}))
scores = {"breakout": [10.0, 50.0, 900.0]}
for g, vs in scores.items():
    for k, s in enumerate(vs, 1):
        d = tmp / "claude-test" / g / f"attempt{k}"
        d.mkdir(parents=True)
        (d / "run.json").write_text(json.dumps({"model": "claude-test", "attempt": k, "score": {"mean": s}}))
sys.argv = ["scoreboard.py", "--logs", "/Users/dhaneshneelamana/lm_understand-logs", "--runs", str(tmp)]
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    scoreboard.main()
print("scoreboard output with attempts [10, 50, 900]:")
print(buf.getvalue())
