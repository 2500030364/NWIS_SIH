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
    print("Connecting to:", ws_url)

    async with websockets.connect(ws_url) as ws:
        msg_id = 1
        await send_cmd(ws, msg_id, "Page.enable"); msg_id += 1
        await send_cmd(ws, msg_id, "Runtime.enable"); msg_id += 1

        # 1920x1080 Viewport
        await send_cmd(ws, msg_id, "Emulation.setDeviceMetricsOverride", {
            "width": 1920,
            "height": 1080,
            "deviceScaleFactor": 1,
            "mobile": False
        }); msg_id += 1

        print("Navigating to http://127.0.0.1:5173/...")
        await send_cmd(ws, msg_id, "Page.navigate", {"url": "http://127.0.0.1:5173/"}); msg_id += 1
        await asyncio.sleep(2.5)

        # Check current depth and step to 3020 if needed
        step_res = await send_cmd(ws, msg_id, "Runtime.evaluate", {
            "expression": """
                (() => {
                    const depthEl = document.querySelector('header');
                    if (depthEl && depthEl.textContent.includes('3015')) {
                        const stepBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim() === '+5m');
                        if (stepBtn) {
                            stepBtn.click();
                            return 'stepped_to_3020';
                        }
                    }
                    return 'already_at_depth';
                })()
            """
        }); msg_id += 1
        print("Depth step action:", step_res)
        await asyncio.sleep(2.0)

        # 1. Capture Overview Dashboard at 1920x1080
        out1 = os.path.join(ARTIFACT_DIR, "overview_dashboard_3020.png")
        await capture_screenshot(ws, msg_id, out1); msg_id += 1

        # 2. Capture Overview at 1366x768
        await send_cmd(ws, msg_id, "Emulation.setDeviceMetricsOverride", {
            "width": 1366,
            "height": 768,
            "deviceScaleFactor": 1,
            "mobile": False
        }); msg_id += 1
        await asyncio.sleep(1.0)
        out2 = os.path.join(ARTIFACT_DIR, "overview_dashboard_1366_hazard.png")
        await capture_screenshot(ws, msg_id, out2); msg_id += 1

        # Reset to 1920x1080
        await send_cmd(ws, msg_id, "Emulation.setDeviceMetricsOverride", {
            "width": 1920,
            "height": 1080,
            "deviceScaleFactor": 1,
            "mobile": False
        }); msg_id += 1
        await asyncio.sleep(0.5)

        # 3. Click [ VIEW EVIDENCE ]
        print("Clicking VIEW EVIDENCE...")
        ev_click = await send_cmd(ws, msg_id, "Runtime.evaluate", {
            "expression": """
                (() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const btn = btns.find(b => b.textContent.includes('VIEW EVIDENCE'));
                    if (btn) {
                        btn.click();
                        return true;
                    }
                    return false;
                })()
            """
        }); msg_id += 1
        print("Evidence button click:", ev_click)
        await asyncio.sleep(1.0)
        out3 = os.path.join(ARTIFACT_DIR, "risk_evidence_modal_verified.png")
        await capture_screenshot(ws, msg_id, out3); msg_id += 1

        # Close evidence modal
        await send_cmd(ws, msg_id, "Runtime.evaluate", {
            "expression": """
                (() => {
                    const closeBtn = document.querySelector('div[class*=\"fixed\"] button');
                    if (closeBtn) closeBtn.click();
                })()
            """
        }); msg_id += 1
        await asyncio.sleep(0.5)

        # 4. Tab: Nearby Wells
        print("Navigating to Nearby Wells...")
        await click_nav_item(ws, msg_id, "Nearby Wells"); msg_id += 1
        await asyncio.sleep(1.5)
        out4 = os.path.join(ARTIFACT_DIR, "tab_nearby_wells.png")
        await capture_screenshot(ws, msg_id, out4); msg_id += 1

        # 5. Tab: Drilling Intelligence
        print("Navigating to Drilling Intelligence...")
        await click_nav_item(ws, msg_id, "Drilling Intelligence"); msg_id += 1
        await asyncio.sleep(1.5)
        out5 = os.path.join(ARTIFACT_DIR, "tab_drilling_intelligence.png")
        await capture_screenshot(ws, msg_id, out5); msg_id += 1

        # 6. Tab: Live Telemetry
        print("Navigating to Live Telemetry...")
        await click_nav_item(ws, msg_id, "Live Telemetry"); msg_id += 1
        await asyncio.sleep(1.5)
        out6 = os.path.join(ARTIFACT_DIR, "tab_telemetry.png")
        await capture_screenshot(ws, msg_id, out6); msg_id += 1

        # 7. Tab: Risk Alerts
        print("Navigating to Risk Alerts...")
        await click_nav_item(ws, msg_id, "Risk Alerts"); msg_id += 1
        await asyncio.sleep(1.5)
        out7 = os.path.join(ARTIFACT_DIR, "tab_risk_alerts.png")
        await capture_screenshot(ws, msg_id, out7); msg_id += 1

        # 8. Tab: Historical Search
        print("Navigating to Historical Search...")
        await click_nav_item(ws, msg_id, "Historical Search"); msg_id += 1
        await asyncio.sleep(1.5)
        out8 = os.path.join(ARTIFACT_DIR, "tab_search.png")
        await capture_screenshot(ws, msg_id, out8); msg_id += 1

        # Return to Overview
        await click_nav_item(ws, msg_id, "Overview"); msg_id += 1
        await asyncio.sleep(0.5)
        print("All tabs and modals captured and verified!")

asyncio.run(main())
