"""Merge all score jsonl files and produce summary stats + merged CSV."""
import json, csv, glob
from collections import defaultdict

# Load original ideas
ideas = {}
with open("modoo_ideas_20260409_1105.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        ideas[int(r["id"])] = r

# Load all scores
all_scores = {}
dup = 0
for path in sorted(glob.glob("scores_*.jsonl")):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception as e:
                print(f"bad line in {path}: {e}")
                continue
            iid = int(obj["id"])
            if iid in all_scores:
                dup += 1
                continue
            all_scores[iid] = obj

print(f"merged {len(all_scores)} scores  (dup skipped: {dup})")
print(f"original ideas: {len(ideas)}")

missing = set(ideas.keys()) - set(all_scores.keys())
extra = set(all_scores.keys()) - set(ideas.keys())
print(f"missing: {len(missing)}   extra: {len(extra)}")
if missing:
    print("missing ids:", sorted(missing)[:20])

# Build merged rows
merged = []
for iid, sc in all_scores.items():
    if iid not in ideas:
        continue
    r = ideas[iid]
    row = {
        "id": iid,
        "division": r["division"],
        "summary": r["summary"],
        "nickname": r["nickname"],
        "likeCount": r["likeCount"],
        "s1": sc["s1"],
        "s2": sc["s2"],
        "s3": sc["s3"],
        "total": sc["s1"] + sc["s2"] + sc["s3"],
        "rationale": sc.get("r", ""),
    }
    merged.append(row)

# Write merged
with open("scores_merged.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(merged[0].keys()))
    w.writeheader()
    w.writerows(merged)

# Summary stats per division
def stats(rows):
    n = len(rows)
    if n == 0:
        return {}
    s1 = [r["s1"] for r in rows]
    s2 = [r["s2"] for r in rows]
    s3 = [r["s3"] for r in rows]
    tot = [r["total"] for r in rows]
    return {
        "n": n,
        "s1_mean": round(sum(s1) / n, 2),
        "s2_mean": round(sum(s2) / n, 2),
        "s3_mean": round(sum(s3) / n, 2),
        "total_mean": round(sum(tot) / n, 2),
        "total_min": min(tot),
        "total_max": max(tot),
    }

tech_rows = [r for r in merged if r["division"] == "TECH"]
local_rows = [r for r in merged if r["division"] == "LOCAL"]

print("\n=== TECH ===")
print(stats(tech_rows))
print("\n=== LOCAL ===")
print(stats(local_rows))

# Distribution histogram by total
def hist(rows):
    h = defaultdict(int)
    for r in rows:
        h[r["total"]] += 1
    out = []
    for t in range(3, 31):
        out.append((t, h[t]))
    return out

print("\n=== TECH total distribution ===")
for t, c in hist(tech_rows):
    bar = "#" * min(60, c // 10)
    print(f"{t:2d}: {c:4d} {bar}")

print("\n=== LOCAL total distribution ===")
for t, c in hist(local_rows):
    bar = "#" * min(60, c // 3)
    print(f"{t:2d}: {c:4d} {bar}")

print(f"\nsaved: scores_merged.csv ({len(merged)} rows)")
