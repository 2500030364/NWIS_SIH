import asyncio
import json
import urllib.request
import base64
import os
import websockets

ARTIFACT_DIR = r"C:\Users\HP\.gemini\antigravity-ide\brain\80957aa0-d884-43ad-8bf6-e8d27dab607a"

async def main():
    targets = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read().decode("utf-8"))
    page_target = next((t for t in targets if t.get("type") == "page" and "5173" in t.get("url", "")), None)
    ws_url = page_target["webSocketDebuggerUrl"]

    async with websockets.connect(ws_url) as ws:
        msg_id = 300
        # Click on a leaflet marker or trigger well selection
        expr = """
            (() => {
                const markers = document.querySelectorAll('.leaflet-marker-icon');
                if (markers.length > 2) {
                    markers[2].dispatchEvent(new MouseEvent('click', { bubbles: true }));
                    return true;
                }
                return false;
            })()
        """
        await ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": expr}}))
        msg_id += 1
        await asyncio.sleep(1.5)

        # Capture screenshot with drawer open
        await ws.send(json.dumps({"id": msg_id, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
        while True:
            res = json.loads(await ws.recv())
            if res.get("id") == msg_id:
                data = base64.b64decode(res["result"]["data"])
                out = os.path.join(ARTIFACT_DIR, "well_detail_drawer_verified.png")
                with open(out, "wb") as f:
                    f.write(data)
                print(f"Captured: {out} ({len(data)} bytes)")
                break

asyncio.run(main())
