"""Sanity check: sample top/mid/bottom from each division and dump for review."""
import csv

with open("scores_merged.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

for r in rows:
    r["total"] = int(r["total"])
    r["s1"] = int(r["s1"])
    r["s2"] = int(r["s2"])
    r["s3"] = int(r["s3"])
    r["likeCount"] = int(r["likeCount"])

# Sample per division
def sample(div, n=10):
    items = sorted([r for r in rows if r["division"] == div], key=lambda x: -x["total"])
    print(f"\n========== {div} TOP {n} ==========")
    for r in items[:n]:
        print(f"  [{r['id']}] T={r['total']} (s1={r['s1']} s2={r['s2']} s3={r['s3']}) ♥{r['likeCount']} | {r['summary'][:80]}")
        print(f"      → {r['rationale']}")
    print(f"\n========== {div} BOTTOM {n} ==========")
    for r in items[-n:]:
        print(f"  [{r['id']}] T={r['total']} (s1={r['s1']} s2={r['s2']} s3={r['s3']}) ♥{r['likeCount']} | {r['summary'][:80]}")
        print(f"      → {r['rationale']}")
    print(f"\n========== {div} MID 5 ==========")
    mid = items[len(items) // 2 - 2 : len(items) // 2 + 3]
    for r in mid:
        print(f"  [{r['id']}] T={r['total']} (s1={r['s1']} s2={r['s2']} s3={r['s3']}) ♥{r['likeCount']} | {r['summary'][:80]}")
        print(f"      → {r['rationale']}")

sample("TECH", 10)
sample("LOCAL", 10)

# Correlation check: like count vs score
from statistics import mean
tech = [r for r in rows if r["division"] == "TECH"]
local = [r for r in rows if r["division"] == "LOCAL"]

def corr(xs, ys):
    n = len(xs)
    if n == 0:
        return 0
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = (sum((x - mx) ** 2 for x in xs)) ** 0.5
    dy = (sum((y - my) ** 2 for y in ys)) ** 0.5
    return num / (dx * dy) if dx * dy else 0

print(f"\n=== Like-count vs total score correlation ===")
print(f"TECH:  r = {corr([r['likeCount'] for r in tech], [r['total'] for r in tech]):.3f}")
print(f"LOCAL: r = {corr([r['likeCount'] for r in local], [r['total'] for r in local]):.3f}")
print("(Low correlation = blinding worked, high = scoring was anchored to popularity)")
