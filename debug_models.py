import requests
import json
r = requests.get("https://openrouter.ai/api/v1/models").json()
free = []
for m in r["data"]:
    p = m.get("pricing", {})
    if m["id"].endswith(":free") or (p.get("prompt") == "0" and p.get("completion") == "0"):
        free.append(m["id"])
print(free[:15])
