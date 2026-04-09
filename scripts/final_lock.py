"""
Run on/after 2026-05-15 to produce the FINAL locked prediction file.

Differs from build_predictions.py:
- Reads final pool counts (public + private) from API
- Computes ACTUAL pass rate per division based on final applicant count
- Replaces speculative scenarios with the single computed cutoff
- Outputs predictions_FINAL_locked.csv + .meta.json + git commit
"""
import csv, json, hashlib, datetime, subprocess, sys, urllib.request, base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

TOTAL_TECH_SLOTS = 4000
TOTAL_LOCAL_SLOTS = 1000

# Get final count from API
def fetch_count():
    req = urllib.request.Request("https://hera-prod.modoo.or.kr/api/v1/startup-idea/count?")
    raw = urllib.request.urlopen(req, timeout=30).read()
    d = json.loads(raw)
    ts = str(d["timestamp"]).ljust(16, "0").encode()
    pt = unpad(AES.new(ts, AES.MODE_CBC, iv=ts).decrypt(base64.b64decode(d["data"])), 16)
    return json.loads(pt.decode("utf-8"))

cnt = fetch_count()
public_n = cnt["publicCount"]
private_n = cnt["privateCount"]
total_n = public_n + private_n
print(f"Final pool: public={public_n}, private={private_n}, total={total_n}")

# Load current scored data
with open("scores_merged.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))
for r in rows:
    r["s1"]=int(r["s1"]); r["s2"]=int(r["s2"]); r["s3"]=int(r["s3"]); r["total"]=int(r["total"])

tech = sorted([r for r in rows if r["division"]=="TECH"], key=lambda x:-x["total"])
local = sorted([r for r in rows if r["division"]=="LOCAL"], key=lambda x:-x["total"])

# Estimate division split assuming private follows public proportions
public_tech = len(tech)
public_local = len(local)
tech_ratio = public_tech / public_n if public_n else 0.82
private_tech_est = round(private_n * tech_ratio)
private_local_est = private_n - private_tech_est
total_tech_est = public_tech + private_tech_est
total_local_est = public_local + private_local_est

# Pass rates (assuming top X% of full pool passes)
tech_pass_rate = TOTAL_TECH_SLOTS / total_tech_est if total_tech_est else 1
local_pass_rate = TOTAL_LOCAL_SLOTS / total_local_est if total_local_est else 1
tech_pass_rate = min(1, tech_pass_rate)
local_pass_rate = min(1, local_pass_rate)

print(f"TECH:  public={public_tech}, est_total={total_tech_est}, slots={TOTAL_TECH_SLOTS}, pass_rate={tech_pass_rate:.3f}")
print(f"LOCAL: public={public_local}, est_total={total_local_est}, slots={TOTAL_LOCAL_SLOTS}, pass_rate={local_pass_rate:.3f}")

# Apply cutoff: top pass_rate fraction of PUBLIC pool gets PASS prediction
# Note: this assumes our public pool quality distribution mirrors private
def cut(items, pr):
    n = len(items)
    pass_n = int(round(n * pr))
    for i, r in enumerate(items):
        r["pred"] = "PASS" if i < pass_n else "FAIL"
        r["rank"] = i + 1
        r["pct_rank"] = round(1 - i / max(1, n - 1), 4)

cut(tech, tech_pass_rate)
cut(local, local_pass_rate)

all_rows = tech + local
fieldnames = ["id","division","total","s1","s2","s3","rank","pct_rank","pred","summary","rationale","likeCount"]
out = "predictions_FINAL_locked.csv"
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    w.writeheader()
    for r in all_rows:
        w.writerow(r)

with open(out, "rb") as f:
    sha256 = hashlib.sha256(f.read()).hexdigest()

meta = {
    "version": "FINAL",
    "locked_at": datetime.datetime.now().isoformat(),
    "deadline": "2026-05-15",
    "total_pool": {"public": public_n, "private": private_n, "total": total_n},
    "tech": {"public": public_tech, "est_total": total_tech_est, "slots": TOTAL_TECH_SLOTS, "pass_rate": tech_pass_rate, "predicted_pass": sum(1 for r in tech if r["pred"]=="PASS")},
    "local": {"public": public_local, "est_total": total_local_est, "slots": TOTAL_LOCAL_SLOTS, "pass_rate": local_pass_rate, "predicted_pass": sum(1 for r in local if r["pred"]=="PASS")},
    "sha256": sha256,
    "scoring_method": "3-axis rubric per division, 1-10 each, scored by general-purpose Claude subagents in parallel batches",
    "blinding": "Confirmed: like-score correlation ≈0.04 (essentially zero)",
    "limitations": [
        "Only 1-line summary used (no detail page, no team info)",
        "Single scoring pass (no variance reduction via multiple samples)",
        "Private pool (~37% of total) is invisible to us",
        "Pass-rate cutoff assumes public/private quality distribution is identical",
    ],
}
with open("predictions_FINAL_locked.meta.json","w",encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

print(f"\n=== FINAL LOCKED ===")
print(f"file: {out}")
print(f"sha256: {sha256}")
print(f"TECH PASS predictions: {meta['tech']['predicted_pass']}/{public_tech}")
print(f"LOCAL PASS predictions: {meta['local']['predicted_pass']}/{public_local}")

# Try to git commit for additional integrity
try:
    subprocess.run(["git","init"], check=False, capture_output=True)
    subprocess.run(["git","add",out,"predictions_FINAL_locked.meta.json"], check=True)
    subprocess.run(["git","commit","-m",f"FINAL prediction lock — sha256:{sha256[:16]}"], check=True)
    print("git commit created")
except Exception as e:
    print(f"git commit skipped: {e}")
