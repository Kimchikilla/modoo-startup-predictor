"""
Incremental update — run periodically until 2026-05-15.

Steps:
1. Re-crawl public pool to a new timestamped CSV
2. Diff against the latest scored snapshot
3. Save new (unscored) items to score_input_NEW_*.txt for next agent run
4. Print delta stats

After this, you should:
- Manually dispatch general-purpose subagents to score the NEW files
- Then re-run merge_scores.py and build_predictions.py
"""
import csv, os, glob, datetime, subprocess, sys

# Re-crawl
print("=== Re-crawling ===")
subprocess.run([sys.executable, "crawl_modoo.py"], check=True)

# Find newest crawl file
crawls = sorted(glob.glob("modoo_ideas_*.csv"))
latest = crawls[-1]
print(f"latest crawl: {latest}")

# Load current scored ids from scores_merged.csv (built by merge_scores.py)
scored_ids = set()
if os.path.exists("scores_merged.csv"):
    with open("scores_merged.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            scored_ids.add(int(r["id"]))
print(f"already scored: {len(scored_ids)}")

# Find new items in latest crawl
new_tech = []
new_local = []
with open(latest, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        iid = int(r["id"])
        if iid in scored_ids:
            continue
        if r["division"] == "TECH":
            new_tech.append(r)
        else:
            new_local.append(r)

print(f"new TECH: {len(new_tech)}   new LOCAL: {len(new_local)}")

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
if new_tech:
    out = f"score_input_NEW_tech_{ts}.txt"
    with open(out, "w", encoding="utf-8") as g:
        for r in new_tech:
            g.write(f"{r['id']}|{r['summary']}\n")
    print(f"  -> {out}")
if new_local:
    out = f"score_input_NEW_local_{ts}.txt"
    with open(out, "w", encoding="utf-8") as g:
        for r in new_local:
            g.write(f"{r['id']}|{r['summary']}\n")
    print(f"  -> {out}")

if not new_tech and not new_local:
    print("nothing new to score.")
else:
    print("\nNEXT STEPS:")
    print("1. Dispatch general-purpose subagent(s) to score the score_input_NEW_*.txt files using prompt_local.md / prompt_tech.md")
    print("2. Save outputs to scores_local_NEW_*.jsonl / scores_tech_NEW_*.jsonl")
    print("3. Run: python merge_scores.py")
    print("4. Run: python build_predictions.py  (this OVERWRITES v1 — for true history, version it)")
