"""Generate compact data.json for the web UI."""
import csv, json

rows = []
with open("predictions_v1_locked.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        rows.append({
            "id": int(r["id"]),
            "d": r["division"],            # TECH or LOCAL
            "t": int(r["total"]),           # 3-30
            "s": [int(r["s1"]), int(r["s2"]), int(r["s3"])],
            "rk": int(r["rank"]),
            "n": int(r["division_n"]),
            "su": (r["summary"] or "").strip()[:300],
            "rt": (r["rationale"] or "").strip()[:120],
            "lk": int(r["likeCount"]),
        })

# Sort: division then by total desc
rows.sort(key=lambda x: (x["d"], -x["t"], x["rk"]))

# Stats
tech = [r for r in rows if r["d"] == "TECH"]
local = [r for r in rows if r["d"] == "LOCAL"]
def stats(items):
    n = len(items)
    return {
        "n": n,
        "mean_total": round(sum(r["t"] for r in items) / n, 2),
        "max_total": max(r["t"] for r in items),
        "min_total": min(r["t"] for r in items),
    }

with open("predictions_v1_locked.meta.json", encoding="utf-8") as f:
    meta = json.load(f)

bundle = {
    "version": "v1",
    "locked_at": meta["locked_at"],
    "sha256": meta["sha256"],
    "deadline": "2026-05-15",
    "slots": {"TECH": 4000, "LOCAL": 1000},
    "stats": {"TECH": stats(tech), "LOCAL": stats(local)},
    "scenarios": [
        {"id": "opt", "name": "낙관 (TECH 82% / LOCAL 94%)", "tech_pr": 0.82, "local_pr": 0.94, "desc": "최종 ~6,000명 가정 (현재 추세)"},
        {"id": "mid", "name": "중도 (TECH 50% / LOCAL 60%)", "tech_pr": 0.50, "local_pr": 0.60, "desc": "최종 ~10,000명 가정"},
        {"id": "pes", "name": "비관 (TECH 30% / LOCAL 40%)", "tech_pr": 0.30, "local_pr": 0.40, "desc": "최종 ~16,000명 가정 (예비창업패키지 50:1 참고)"},
    ],
    "rows": rows,
}

with open("site/data.json", "w", encoding="utf-8") as f:
    json.dump(bundle, f, ensure_ascii=False, separators=(",", ":"))

import os
size_kb = os.path.getsize("site/data.json") / 1024
print(f"data.json: {len(rows)} rows, {size_kb:.1f} KB")
print(f"TECH stats: {bundle['stats']['TECH']}")
print(f"LOCAL stats: {bundle['stats']['LOCAL']}")
