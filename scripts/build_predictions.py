"""Build prediction file with multiple cutoff scenarios + SHA256 lock."""
import csv, json, hashlib, datetime

with open("scores_merged.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))
for r in rows:
    r["s1"] = int(r["s1"]); r["s2"] = int(r["s2"]); r["s3"] = int(r["s3"])
    r["total"] = int(r["total"])
    r["likeCount"] = int(r["likeCount"])

# Rank within division
def rank_division(div):
    items = sorted([r for r in rows if r["division"] == div], key=lambda x: -x["total"])
    n = len(items)
    for i, r in enumerate(items):
        r["rank"] = i + 1
        r["pct_rank"] = round(1 - (i / max(1, n - 1)), 4)  # 1=best, 0=worst
        r["division_n"] = n
    return items

tech = rank_division("TECH")
local = rank_division("LOCAL")

# Tied-rank handling: same total → same rank
def fix_ties(items):
    prev_total = None
    prev_rank = None
    for i, r in enumerate(items):
        if r["total"] == prev_total:
            r["rank"] = prev_rank
        else:
            prev_total = r["total"]
            prev_rank = r["rank"]
fix_ties(tech)
fix_ties(local)

# Define cutoff scenarios
# Each scenario: (name, tech_pass_rate, local_pass_rate, description)
scenarios = [
    ("optimistic_82_94", 0.82, 0.94, "User-stated baseline: TECH 82%/LOCAL 94% pass (assumes ~6000 final applicants)"),
    ("medium_50_60",     0.50, 0.60, "Medium competition: ~10000 final applicants"),
    ("pessimistic_30_40",0.30, 0.40, "High competition: ~16000 final applicants"),
]

def apply_cutoff(items, pass_rate, label):
    n = len(items)
    pass_count = int(round(n * pass_rate))
    for i, r in enumerate(items):
        r[f"pred_{label}"] = "PASS" if i < pass_count else "FAIL"

for name, tech_pr, local_pr, _ in scenarios:
    apply_cutoff(tech, tech_pr, name)
    apply_cutoff(local, local_pr, name)

# Combine
all_rows = tech + local

# Output
fieldnames = ["id","division","total","s1","s2","s3","rank","pct_rank","division_n","likeCount","summary","rationale"] + [f"pred_{s[0]}" for s in scenarios]
with open("predictions_v1_locked.csv","w",encoding="utf-8-sig",newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    w.writeheader()
    for r in all_rows:
        w.writerow(r)

# Compute hash
with open("predictions_v1_locked.csv","rb") as f:
    sha256 = hashlib.sha256(f.read()).hexdigest()

# Metadata file
meta = {
    "version": "v1",
    "locked_at": datetime.datetime.now().isoformat(),
    "data_snapshot": "modoo_ideas_20260409_1105.csv",
    "total_scored": len(all_rows),
    "tech_n": len(tech),
    "local_n": len(local),
    "sha256": sha256,
    "scoring_method": "5 dimensions per rubric (LOCAL: 차별성/지역가치/성장가능성, TECH: 차별성/사업성/성장가능성), each 1-10, 1 pass, 10 general-purpose subagents in parallel",
    "blinding": "Nicknames, like counts, division tags removed from input. Confirmed by like-score correlation: TECH r=0.036, LOCAL r=0.049",
    "cutoff_scenarios": [{"name": n, "tech_pass": t, "local_pass": l, "desc": d} for n, t, l, d in scenarios],
    "missing": "1 idea (id 12724) was duplicated in agent output and re-scored manually by main assistant",
    "deadline": "2026-05-15 — recruitment still open at lock time, ~5990 total applicants (3797 public + 2193 private). Re-lock planned at deadline with final snapshot.",
    "evaluation_metrics_planned": ["Precision/Recall (per scenario)", "AUROC", "Brier score", "Calibration plot", "FAIL-class F1"],
}

with open("predictions_v1_locked.meta.json","w",encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

print(f"=== LOCKED ===")
print(f"file:   predictions_v1_locked.csv")
print(f"sha256: {sha256}")
print(f"rows:   {len(all_rows)} (TECH {len(tech)}, LOCAL {len(local)})")
print(f"meta:   predictions_v1_locked.meta.json")

# Print pass count per scenario
print("\n=== Cutoff scenarios ===")
for name, tech_pr, local_pr, desc in scenarios:
    tn = sum(1 for r in tech if r[f"pred_{name}"]=="PASS")
    ln = sum(1 for r in local if r[f"pred_{name}"]=="PASS")
    print(f"  {name}: TECH {tn}/{len(tech)} pass, LOCAL {ln}/{len(local)} pass — {desc}")
