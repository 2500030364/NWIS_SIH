import urllib.request
import json

def test_url(url, name):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req)
        body = res.read().decode('utf-8')
        print(f"[OK] {name}: HTTP {res.getcode()} (length: {len(body)})")
        return body
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return None

print("=== TESTING BACKEND APIS ===")
test_url("http://127.0.0.1:8000/api/health", "Health")
ev_count = test_url("http://127.0.0.1:8000/api/events/count", "Events Count")
print("Events count response:", ev_count)

reps = test_url("http://127.0.0.1:8000/api/reports?limit=5", "Reports List")
if reps:
    data = json.loads(reps)
    print(f"Reports sample count: {len(data)}, first: {data[0]['report_name']} ({data[0]['report_type']}) from {data[0]['well_name']}")

w1 = test_url("http://127.0.0.1:8000/api/wells/1", "Well 1 Details")
if w1:
    w1_data = json.loads(w1)
    print(f"Well 1 Status: {w1_data.get('status')} | Name: {w1_data.get('well_name')}")

risks = test_url("http://127.0.0.1:8000/api/risks/1?depth=3020", "Risks Well 1")
if risks:
    r_data = json.loads(risks)
    print(f"Risks count: {len(r_data.get('risks', []))}, top: {r_data.get('risks', [])[0]['title']} ({r_data.get('risks', [])[0]['level']})")

print("\n=== TESTING FRONTEND DEV SERVER & VITE PROXY ===")
fe = test_url("http://127.0.0.1:5173/", "Frontend Root")
if fe:
    print("Frontend HTML contains '<div id=\"root\">':", '<div id="root">' in fe)

fe_proxy = test_url("http://127.0.0.1:5173/api/events/count", "Frontend Proxy to /api/events/count")
print("Proxy response:", fe_proxy)
