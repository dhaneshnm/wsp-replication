# Raw analysis output

This folder is the raw output of the Claude Code agent workflows run on 2026-11-06. It is committed as-is so the
process can be checked. It has not been curated or code-reviewed.

| Path | What it is |
|---|---|
| `harness_audit.json` | Harness audit: 6 finders, 3 verifiers per finding (51 agents). Every candidate, vote and reason |
| `analysis_breakout_asterix.json`, `analysis_seaquest.json` | Reply analysis: per attempt, 1 analyst and 2 checkers, plus a synthesis per game (30 agents). Every claim and verdict |
| `scripts/<game>_attempt<N>/` | Working folder of the analyst for that attempt, with its checkers' subfolders |
| `scripts/<game>_attempt<N>_verify/`, `scripts/*_synth/` | Working folders of the checkers and the per-game synthesis agent |
| `audit_scripts/` | Working folder of the harness-audit agents |

Things to know before using it:

- `RESULTS.md` reports only claims that no checker refuted. Some scripts here back claims that were later refuted. The
  JSON files say which.
- All agents were Claude Opus 5.5. No human reviewed the mechanism claims.
- Large intermediate files (over 2 MB: episode traces and pickles) were deleted to keep the repo small. A few other
  files were removed before publishing: verbatim copies of MinAtar's GPL source, a test fixture that held a truncated
  copy of Astra's reply text, a profiler dump, a broken link, and one output the agent had marked invalid. Some
  scripts and JSON text still refer to these files.
- Scripts hard-code the paths used during the run. To rerun one, map them like this:

  | Path in the scripts | Meaning |
  |---|---|
  | `/Users/<user>/projects/wsp-replication` | this repository's root |
  | `/Users/<user>/lm_understand-logs` | a clone of https://github.com/RikiyaT/lm_understand-logs |
  | `/private/tmp/claude-501/<session>/scratchpad/analysis/<X>` | `runs/analysis/scripts/<X>` |
  | `/private/tmp/claude-501/<session>/scratchpad/audit` | `runs/analysis/audit_scripts` |
