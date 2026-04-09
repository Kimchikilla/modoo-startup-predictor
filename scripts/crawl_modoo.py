import base64, json, csv, time, urllib.request
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

BASE = "https://hera-prod.modoo.or.kr/api/v1/startup-idea"
SIZE = 100

def fetch(page):
    req = urllib.request.Request(f"{BASE}?page={page}&size={SIZE}")
    raw = urllib.request.urlopen(req, timeout=30).read()
    d = json.loads(raw)
    ts = str(d["timestamp"]).ljust(16, "0").encode()
    pt = unpad(AES.new(ts, AES.MODE_CBC, iv=ts).decrypt(base64.b64decode(d["data"])), 16)
    return json.loads(pt.decode("utf-8"))

def fetch_count():
    req = urllib.request.Request(f"https://hera-prod.modoo.or.kr/api/v1/startup-idea/count?")
    raw = urllib.request.urlopen(req, timeout=30).read()
    d = json.loads(raw)
    ts = str(d["timestamp"]).ljust(16, "0").encode()
    pt = unpad(AES.new(ts, AES.MODE_CBC, iv=ts).decrypt(base64.b64decode(d["data"])), 16)
    return json.loads(pt.decode("utf-8"))

print("count:", fetch_count())

rows = []
page = 0
while True:
    items = fetch(page)
    if not items:
        break
    for it in items:
        rows.append({
            "id": it.get("id"),
            "division": it.get("division"),
            "summary": (it.get("summary") or "").replace("\r", " ").replace("\n", " ").strip(),
            "nickname": (it.get("applicant") or {}).get("nickname", ""),
            "likeCount": it.get("likeCount", 0),
            "createdAt": it.get("createdAt", ""),
        })
    print(f"page {page}: +{len(items)} (total {len(rows)})")
    if len(items) < SIZE:
        break
    page += 1
    time.sleep(0.2)

import datetime
out_name = f"modoo_ideas_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv"
with open(out_name, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "division", "summary", "nickname", "likeCount", "createdAt"])
    w.writeheader()
    w.writerows(rows)

print(f"saved {len(rows)} rows -> {out_name}")
