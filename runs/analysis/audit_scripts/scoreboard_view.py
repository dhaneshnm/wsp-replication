# Read-only: what scoreboard.py's glob would aggregate per game, plus stop_reason (which scoreboard ignores).
import json, pathlib
runs = pathlib.Path("/Users/dhaneshneelamana/projects/wsp-replication/runs")
for game in ["breakout", "seaquest", "asterix"]:
    for f in sorted(runs.glob(f"*/{game}/attempt*/run.json")):
        r = json.loads(f.read_text())
        u = r["usage"]
        print(game, f.parent.name, "score", r["score"]["mean"], "stop_reason", u.get("stop_reason"),
              "output_tokens", u.get("output_tokens"), "thinking", (u.get("output_tokens_details") or {}).get("thinking_tokens"),
              "parse", r["parse"])
