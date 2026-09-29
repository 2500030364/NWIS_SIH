import asyncio
import json
import urllib.request
import base64
import os
import websockets

ARTIFACT_DIR = r"C:\Users\HP\.gemini\antigravity-ide\brain\80957aa0-d884-43ad-8bf6-e8d27dab607a"

async def send_cmd(ws, msg_id, method, params=None):
    payload = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(payload))
    while True:
        res = json.loads(await ws.recv())
        if res.get("id") == msg_id:
            return res.get("result", {})

async def capture_screenshot(ws, msg_id, filepath):
    res = await send_cmd(ws, msg_id, "Page.captureScreenshot", {"format": "png"})
    img_data = base64.b64decode(res["data"])
    with open(filepath, "wb") as f:
        f.write(img_data)
    print(f"Captured: {filepath} ({len(img_data)} bytes)")

async def click_nav_item(ws, msg_id, label_text):
    expr = f"""
        (() => {{
            const buttons = Array.from(document.querySelectorAll('aside nav button'));
            const target = buttons.find(b => b.textContent.includes('{label_text}'));
            if (target) {{
                target.click();
                return true;
            }}
            return false;
        }})()
    """
    res = await send_cmd(ws, msg_id, "Runtime.evaluate", {"expression": expr})
    return res

async def main():
    targets_json = urllib.request.urlopen("http://127.0.0.1:9222/json").read().decode("utf-8")
    targets = json.loads(targets_json)
    page_target = next((t for t in targets if t.get("type") == "page" and "5173" in t.get("url", "")), None)
    if not page_target:
        page_target = next((t for t in targets if t.get("type") == "page"), None)
    
    ws_url = page_target["webSocketDebuggerUrl"]

    async with websockets.connect(ws_url) as ws:
        msg_id = 100
        await send_cmd(ws, msg_id, "Page.enable"); msg_id += 1
        await send_cmd(ws, msg_id, "Runtime.enable"); msg_id += 1

        # Viewport: 1920x1080
        await send_cmd(ws, msg_id, "Emulation.setDeviceMetricsOverride", {
            "width": 1920,
            "height": 1080,
            "deviceScaleFactor": 1,
            "mobile": False
        }); msg_id += 1

        # Navigate fresh to http://127.0.0.1:5173/
        await send_cmd(ws, msg_id, "Page.navigate", {"url": "http://127.0.0.1:5173/"}); msg_id += 1
        await asyncio.sleep(2.0)

        # 1. Nearby Wells Tab
        print("Clicking Nearby Wells...")
        await click_nav_item(ws, msg_id, "Nearby Wells"); msg_id += 1
        await asyncio.sleep(1.5)
        out1 = os.path.join(ARTIFACT_DIR, "tab_nearby_wells.png")
        await capture_screenshot(ws, msg_id, out1); msg_id += 1

        # 2. Drilling Intelligence Tab
        print("Clicking Drilling Intelligence...")
        await click_nav_item(ws, msg_id, "Drilling Intelligence"); msg_id += 1
        await asyncio.sleep(1.5)
        out2 = os.path.join(ARTIFACT_DIR, "tab_drilling_intelligence.png")
        await capture_screenshot(ws, msg_id, out2); msg_id += 1

        # 3. Live Telemetry Tab
        print("Clicking Live Telemetry...")
        await click_nav_item(ws, msg_id, "Live Telemetry"); msg_id += 1
        await asyncio.sleep(1.5)
        out3 = os.path.join(ARTIFACT_DIR, "tab_telemetry.png")
        await capture_screenshot(ws, msg_id, out3); msg_id += 1

        # 4. Risk Alerts Tab
        print("Clicking Risk Alerts...")
        await click_nav_item(ws, msg_id, "Risk Alerts"); msg_id += 1
        await asyncio.sleep(1.5)
        out4 = os.path.join(ARTIFACT_DIR, "tab_risk_alerts.png")
        await capture_screenshot(ws, msg_id, out4); msg_id += 1

        # 5. Historical Search Tab with a sample search
        print("Clicking Historical Search...")
        await click_nav_item(ws, msg_id, "Historical Search"); msg_id += 1
        await asyncio.sleep(1.5)
        
        # Type 'mud loss in Demo-Barail' and click search
        await send_cmd(ws, msg_id, "Runtime.evaluate", {
            "expression": """
                (() => {
                    const input = document.querySelector('input[type=\"text\"]');
                    if (input) {
                        input.value = 'mud loss in Demo-Barail';
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                    const searchBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim().toLowerCase().includes('search'));
                    if (searchBtn) searchBtn.click();
                })()
            """
        }); msg_id += 1
        await asyncio.sleep(2.0)
        out5 = os.path.join(ARTIFACT_DIR, "tab_search_results.png")
        await capture_screenshot(ws, msg_id, out5); msg_id += 1

        # Return to Overview
        await click_nav_item(ws, msg_id, "Overview"); msg_id += 1
        await asyncio.sleep(0.5)
        print("All tabs captured successfully!")

asyncio.run(main())
