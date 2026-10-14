import os
import sys
import json
import time
import subprocess
import urllib.request
import asyncio
import base64
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
VIEWPORTS = [375, 768, 1280, 1920, 2560]
SCREENSHOTS_DIR = os.path.join("docs", "screenshots")

async def run_screenshots():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    
    # Launch Chrome
    port = 9222
    user_data = os.path.abspath("tmp_chrome_profile")
    cmd = [
        CHROME_PATH,
        "--headless=new",
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data}",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    proc = subprocess.Popen(cmd)
    time.sleep(2)
    
    try:
        # Get target websocket URL
        new_req = urllib.request.Request(f"http://127.0.0.1:{port}/json/new?http://localhost:3000/index.html", method="PUT")
        with urllib.request.urlopen(new_req) as resp:
            tab_info = json.loads(resp.read().decode())
        ws_url = tab_info["webSocketDebuggerUrl"]
        
        async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
            msg_id = 0
            
            async def send_cmd(method, params=None):
                nonlocal msg_id
                msg_id += 1
                payload = {"id": msg_id, "method": method, "params": params or {}}
                await ws.send(json.dumps(payload))
                while True:
                    resp_raw = await ws.recv()
                    resp = json.loads(resp_raw)
                    if resp.get("id") == msg_id:
                        return resp.get("result", {})
            
            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")
            await send_cmd("Console.enable")
            
            # Wait for page to load completely
            await asyncio.sleep(1.5)
            
            # Check console errors
            eval_res = await send_cmd("Runtime.evaluate", {
                "expression": "console.error.toString()"
            })
            
            for w in VIEWPORTS:
                h = 900 if w >= 768 else 812
                # Override viewport
                await send_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": w,
                    "height": h,
                    "deviceScaleFactor": 1,
                    "mobile": (w <= 768)
                })
                await send_cmd("Emulation.setVisibleSize", {"width": w, "height": h})
                await asyncio.sleep(0.3)
                
                # Check horizontal scroll
                scroll_check = await send_cmd("Runtime.evaluate", {
                    "expression": "document.documentElement.scrollWidth > document.documentElement.clientWidth"
                })
                has_h_scroll = scroll_check.get("result", {}).get("value", False)
                print(f"Viewport {w}px: horizontal scroll = {has_h_scroll}")
                
                # Get hero section bounding box
                box_res = await send_cmd("Runtime.evaluate", {
                    "expression": """
                    (() => {
                        const el = document.querySelector('.hero-slider-section');
                        if (!el) return null;
                        const r = el.getBoundingClientRect();
                        return { x: r.left, y: r.top, width: r.width, height: r.height };
                    })()
                    """,
                    "returnByValue": True
                })
                hero_box = box_res.get("result", {}).get("value")
                
                for slide_idx in range(5):
                    # Click dot for this slide
                    await send_cmd("Runtime.evaluate", {
                        "expression": f"""
                        (() => {{
                            const dots = document.querySelectorAll('.slider-dot');
                            if (dots[{slide_idx}]) dots[{slide_idx}].click();
                        }})()
                        """
                    })
                    # Wait for transition (0.4s)
                    await asyncio.sleep(0.6)
                    
                    # Capture screenshot of hero section
                    clip_param = None
                    if hero_box:
                        clip_param = {
                            "x": 0,
                            "y": float(hero_box["y"]),
                            "width": float(w),
                            "height": float(hero_box["height"]),
                            "scale": 1
                        }
                    
                    shot_params = {"format": "png"}
                    if clip_param:
                        shot_params["clip"] = clip_param
                        shot_params["captureBeyondViewport"] = False
                    
                    shot_res = await send_cmd("Page.captureScreenshot", shot_params)
                    b64_data = shot_res.get("data")
                    if b64_data:
                        out_name = f"slide_{slide_idx + 1}_{w}px.png"
                        out_path = os.path.join(SCREENSHOTS_DIR, out_name)
                        with open(out_path, "wb") as f_out:
                            f_out.write(base64.b64decode(b64_data))
                        print(f"Saved: {out_path} ({os.path.getsize(out_path)} bytes)")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    asyncio.run(run_screenshots())
