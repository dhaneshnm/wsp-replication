"""What run_editor.py would score if Claude's reply were cut off by max_tokens (stop_reason 'max_tokens')
or empty (stop_reason 'refusal'). Uses Astra's own breakout reply, truncated, as the stand-in."""
import pathlib
import sys

sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp  # noqa: E402

ans = pathlib.Path("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/breakout/reply/answer.md").read_text()
start = ans.index("```edits")
end = ans.index("```", start + 8)
cases = {
    "full reply": ans,
    "cut 75% into the edits block (no closing fence)": ans[: start + int(0.75 * (end - start))],
    "cut right before the closing fence": ans[:end],
    "empty text (refusal / all tokens spent thinking)": "",
}
for name, text in cases.items():
    net, rep = wsp.apply_edits(text)
    nz = int(sum((v != 0).sum() for v in net.values()))
    print(f"{name:<52} applied {rep.applied}/{rep.statements}, nonzero {nz}, errors {rep.errors[:1]}")
