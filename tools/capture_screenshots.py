import os
import sys
import json
import time
import subprocess
import urllib.request
import asyncio
import base64
import websockets
from PIL import Image
import numpy as np

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
VIEWPORTS = [375, 768, 1280, 1920, 2560]
SCREENSHOTS_DIR = os.path.join("docs", "screenshots")

async def run_screenshots():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    
    # Launch Chrome
    port = 9224
    user_data = os.path.abspath("tmp_chrome_profile_shots")
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
            await asyncio.sleep(1.5)

            # Disable smooth scrolling for instant positioning
            await send_cmd("Runtime.evaluate", {
                "expression": "document.documentElement.style.scrollBehavior = 'auto';"
            })
            
            # 1. Check 320px horizontal scroll
            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 320,
                "height": 600,
                "deviceScaleFactor": 1,
                "mobile": True
            })
            await send_cmd("Emulation.setVisibleSize", {"width": 320, "height": 600})
            await asyncio.sleep(0.3)
            scroll_check_320 = await send_cmd("Runtime.evaluate", {
                "expression": "document.documentElement.scrollWidth > document.documentElement.clientWidth"
            })
            has_h_scroll_320 = scroll_check_320.get("result", {}).get("value", False)
            print(f"Viewport 320px: horizontal scroll = {has_h_scroll_320}")

            # 2. Check desktop navbar height at 1280px
            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 1280,
                "height": 900,
                "deviceScaleFactor": 1,
                "mobile": False
            })
            await send_cmd("Emulation.setVisibleSize", {"width": 1280, "height": 900})
            await asyncio.sleep(0.3)
            nav_height_res = await send_cmd("Runtime.evaluate", {
                "expression": "document.querySelector('.nav-bar').getBoundingClientRect().height"
            })
            nav_height = nav_height_res.get("result", {}).get("value")
            header_height_res = await send_cmd("Runtime.evaluate", {
                "expression": "document.querySelector('.site-header').getBoundingClientRect().height"
            })
            header_height = header_height_res.get("result", {}).get("value")
            print(f"Desktop 1280px: .nav-bar height = {nav_height:.1f}px, .site-header height = {header_height:.1f}px")

            # 3. Capture header and footer screenshots at 375, 768, 1280px
            for w in [375, 768, 1280]:
                h = 900 if w >= 768 else 812
                await send_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": w,
                    "height": h,
                    "deviceScaleFactor": 1,
                    "mobile": (w <= 768)
                })
                await send_cmd("Emulation.setVisibleSize", {"width": w, "height": h})
                await send_cmd("Runtime.evaluate", {"expression": "window.scrollTo(0, 0);"})
                await asyncio.sleep(0.3)

                # Header box in page coords
                hdr_box = (await send_cmd("Runtime.evaluate", {
                    "expression": """
                    (() => {
                        const el = document.querySelector('.site-header');
                        if (!el) return null;
                        const r = el.getBoundingClientRect();
                        return { x: r.left + window.pageXOffset, y: r.top + window.pageYOffset, width: r.width, height: r.height };
                    })()
                    """,
                    "returnByValue": True
                })).get("result", {}).get("value")

                if hdr_box:
                    shot = await send_cmd("Page.captureScreenshot", {
                        "format": "png",
                        "clip": {
                            "x": float(hdr_box["x"]),
                            "y": float(hdr_box["y"]),
                            "width": float(hdr_box["width"]),
                            "height": float(hdr_box["height"]),
                            "scale": 1
                        },
                        "captureBeyondViewport": True
                    })
                    if shot.get("data"):
                        out_p = os.path.join(SCREENSHOTS_DIR, f"header_{w}px.png")
                        with open(out_p, "wb") as f:
                            f.write(base64.b64decode(shot["data"]))
                        print(f"Saved: {out_p}")

                # Footer box in page coords
                ftr_box = (await send_cmd("Runtime.evaluate", {
                    "expression": """
                    (() => {
                        const el = document.querySelector('.site-footer');
                        if (!el) return null;
                        const r = el.getBoundingClientRect();
                        return { x: r.left + window.pageXOffset, y: r.top + window.pageYOffset, width: r.width, height: r.height };
                    })()
                    """,
                    "returnByValue": True
                })).get("result", {}).get("value")

                if ftr_box:
                    shot = await send_cmd("Page.captureScreenshot", {
                        "format": "png",
                        "clip": {
                            "x": float(ftr_box["x"]),
                            "y": float(ftr_box["y"]),
                            "width": float(ftr_box["width"]),
                            "height": float(ftr_box["height"]),
                            "scale": 1
                        },
                        "captureBeyondViewport": True
                    })
                    if shot.get("data"):
                        out_p = os.path.join(SCREENSHOTS_DIR, f"footer_{w}px.png")
                        with open(out_p, "wb") as f:
                            f.write(base64.b64decode(shot["data"]))
                        print(f"Saved: {out_p}")

            # 4. Check 2x display sharpness for header at 1280px (deviceScaleFactor = 2)
            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 1280,
                "height": 900,
                "deviceScaleFactor": 2,
                "mobile": False
            })
            await send_cmd("Emulation.setVisibleSize", {"width": 1280, "height": 900})
            await send_cmd("Runtime.evaluate", {"expression": "window.scrollTo(0, 0);"})
            await asyncio.sleep(0.4)
            hdr_box_2x = (await send_cmd("Runtime.evaluate", {
                "expression": """
                (() => {
                    const el = document.querySelector('.site-header');
                    if (!el) return null;
                    const r = el.getBoundingClientRect();
                    return { x: r.left + window.pageXOffset, y: r.top + window.pageYOffset, width: r.width, height: r.height };
                })()
                """,
                "returnByValue": True
            })).get("result", {}).get("value")
            if hdr_box_2x:
                shot_2x = await send_cmd("Page.captureScreenshot", {
                    "format": "png",
                    "clip": {
                        "x": float(hdr_box_2x["x"]),
                        "y": float(hdr_box_2x["y"]),
                        "width": float(hdr_box_2x["width"]),
                        "height": float(hdr_box_2x["height"]),
                        "scale": 2
                    },
                    "captureBeyondViewport": True
                })
                if shot_2x.get("data"):
                    out_p = os.path.join(SCREENSHOTS_DIR, "header_1280px_2x.png")
                    with open(out_p, "wb") as f:
                        f.write(base64.b64decode(shot_2x["data"]))
                    print(f"Saved: {out_p}")

            # 5. Capture all 5 hero slides across all 5 viewports
            for w in VIEWPORTS:
                h = 900 if w >= 768 else 812
                await send_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": w,
                    "height": h,
                    "deviceScaleFactor": 1,
                    "mobile": (w <= 768)
                })
                await send_cmd("Emulation.setVisibleSize", {"width": w, "height": h})
                await send_cmd("Runtime.evaluate", {"expression": "window.scrollTo(0, 0);"})
                await asyncio.sleep(0.3)
                
                scroll_check = await send_cmd("Runtime.evaluate", {
                    "expression": "document.documentElement.scrollWidth > document.documentElement.clientWidth"
                })
                has_h_scroll = scroll_check.get("result", {}).get("value", False)
                print(f"Viewport {w}px: horizontal scroll = {has_h_scroll}")
                
                hero_box = (await send_cmd("Runtime.evaluate", {
                    "expression": """
                    (() => {
                        const el = document.querySelector('.hero-slider-section');
                        if (!el) return null;
                        const r = el.getBoundingClientRect();
                        return { x: r.left + window.pageXOffset, y: r.top + window.pageYOffset, width: r.width, height: r.height };
                    })()
                    """,
                    "returnByValue": True
                })).get("result", {}).get("value")
                
                for slide_idx in range(5):
                    await send_cmd("Runtime.evaluate", {
                        "expression": f"""
                        (() => {{
                            const dots = document.querySelectorAll('.slider-dot');
                            if (dots[{slide_idx}]) dots[{slide_idx}].click();
                        }})()
                        """
                    })
                    await asyncio.sleep(0.6)
                    
                    shot_res = await send_cmd("Page.captureScreenshot", {
                        "format": "png",
                        "clip": {
                            "x": float(hero_box["x"]),
                            "y": float(hero_box["y"]),
                            "width": float(hero_box["width"]),
                            "height": float(hero_box["height"]),
                            "scale": 1
                        },
                        "captureBeyondViewport": True
                    })
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
