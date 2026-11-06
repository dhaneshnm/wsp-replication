"""Sensitivity check: would a stricter reading of the spec change any network?

The harness audit (2026-11-06) confirmed three edge cases where wsp.apply_edits departs from the prompt's
reading rules ("one statement per line ... a statement that cannot be read is skipped (the others still apply)";
"Only the LAST edits block of your reply is read"):
  1. one unbalanced '[' glues every later line onto that statement, so all of them are lost;
  2. three backticks inside a '#' comment end the block early;
  3. a final block with no closing fence (cut-off reply) is ignored, so an earlier block or nothing is read.
This script re-reads every reply with a reader that fixes all three and compares the networks with the ones scored.
If no network differs, the scores stand.

Usage: python -I reparse_check.py --logs ~/lm_understand-logs [--runs runs runs/cap128k]
"""
import argparse
import pathlib
import re
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import wsp  # noqa: E402

START = re.compile(r"^\s*(W1|b1|W2|b2|W3|b3)\s*\[")


def last_block(text: str):
    """Last block opened by a line ```edits; it ends at a line that is only ``` (or at the end of the reply)."""
    opens = list(re.finditer(r"^[ \t]*```edits[ \t]*\r?$", text, re.M))
    if not opens:
        return None, False
    rest = text[opens[-1].end():].lstrip("\r\n")
    end = re.search(r"^[ \t]*```[ \t]*\r?$", rest, re.M)
    return (rest[:end.start()] if end else rest), end is None


def statements(block: str):
    out, buf = [], ""
    for raw in block.splitlines():
        line = wsp._strip_comment(raw).rstrip()
        if buf and START.match(line):  # a line that starts a statement always starts a new one
            out.append(buf.strip())
            buf = ""
        if not line.strip() and not buf:
            continue
        buf = f"{buf} {line}" if buf else line
        if buf.count("[") - buf.count("]") <= 0:
            out.append(buf.strip())
            buf = ""
    if buf.strip():
        out.append(buf.strip())
    return out


def strict_apply(text: str):
    block, cut = last_block(text)
    if block is None:
        return wsp.zero_net(), 0, 0, cut
    stmts = statements(block)
    if cut and stmts:
        stmts = stmts[:-1]  # the last statement of a cut-off block may be incomplete
    fenced = "```edits\n" + "\n".join(stmts) + "\n```"
    net, rep = wsp.apply_edits(fenced)  # same statement semantics as the harness, one statement per entry
    return net, rep.applied, rep.statements, cut


def diff(a, b):
    return max(float(np.abs(a[k] - b[k]).max()) for k in wsp.SHAPES)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--logs", required=True)
    ap.add_argument("--runs", nargs="+", default=["runs", "runs/cap128k"])
    a = ap.parse_args()

    exp = pathlib.Path(a.logs).expanduser() / "exp5_write_from_scratch"
    print("Paper replies (must still give hand.npz exactly):")
    for g in ["breakout", "seaquest", "asterix"]:
        net, ok, n, cut = strict_apply((exp / "runs" / g / "reply" / "answer.md").read_text())
        print(f"  {g}: {ok}/{n} statements, cut_off={cut}, max |strict - hand.npz| = {diff(net, wsp.load_npz(str(exp / 'networks' / g / 'hand.npz'))):.1e}")

    print("Claude replies (strict reader vs the network that was scored):")
    changed = 0
    for root in a.runs:
        for f in sorted(pathlib.Path(root).glob("*/*/attempt*/answer.md")):
            text = f.read_text()
            scored = wsp.load_npz(str(f.parent / "net.npz"))
            harness, rep = wsp.apply_edits(text)
            net, ok, n, cut = strict_apply(text)
            d = diff(net, scored)
            changed += d > 0
            print(f"  {f.parent}: harness {rep.applied}/{rep.statements}, strict {ok}/{n}, cut_off={cut}, "
                  f"max |strict - scored| = {d:.1e}{'  <-- DIFFERS' if d > 0 else ''}")
    print(f"{changed} network(s) differ." + (" Re-score those." if changed else " Scores stand."))


if __name__ == "__main__":
    main()
