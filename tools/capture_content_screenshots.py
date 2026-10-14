import os
import sys
import json
import time
import subprocess
import urllib.request
import asyncio
import base64
import websockets
import shutil

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SCREENSHOTS_DIR = os.path.join("docs", "screenshots")

async def capture_all():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    port = 9225
    user_data = os.path.abspath("tmp_chrome_content_shots")

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

    console_errors = []

    try:
        new_req = urllib.request.Request(f"http://127.0.0.1:{port}/json/new", method="PUT")
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
                    if resp.get("method") == "Runtime.exceptionThrown":
                        console_errors.append(resp)
                    if resp.get("id") == msg_id:
                        return resp.get("result", {})

            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")
            await send_cmd("Console.enable")

            # 1. Capture Home Sections (Categories, About, Why Us) at 1280px and 375px
            await send_cmd("Page.navigate", {"url": "http://localhost:3000/index.html"})
            await asyncio.sleep(1.0)
            await send_cmd("Runtime.evaluate", {
                "expression": "document.documentElement.style.scrollBehavior = 'auto';"
            })

            home_sections = [
                ("categories-section", "home_categories"),
                ("about-preview-section", "home_who_we_are"),
                ("why-us-section", "home_why_choose_us")
            ]

            for width in [1280, 375]:
                height = 900 if width == 1280 else 812
                await send_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": width,
                    "height": height,
                    "deviceScaleFactor": 1,
                    "mobile": (width == 375)
                })
                await send_cmd("Emulation.setVisibleSize", {"width": width, "height": height})
                await asyncio.sleep(0.3)

                for selector_cls, name in home_sections:
                    box = (await send_cmd("Runtime.evaluate", {
                        "expression": f"""
                        (() => {{
                            const el = document.querySelector('.{selector_cls}');
                            if (!el) return null;
                            const r = el.getBoundingClientRect();
                            return {{ x: r.left + window.pageXOffset, y: r.top + window.pageYOffset, width: r.width, height: r.height }};
                        }})()
                        """,
                        "returnByValue": True
                    })).get("result", {}).get("value")

                    if box:
                        shot = await send_cmd("Page.captureScreenshot", {
                            "format": "png",
                            "clip": {
                                "x": float(box["x"]),
                                "y": float(box["y"]),
                                "width": float(box["width"]),
                                "height": float(box["height"]),
                                "scale": 1
                            },
                            "captureBeyondViewport": True
                        })
                        if shot.get("data"):
                            out_p = os.path.join(SCREENSHOTS_DIR, f"{name}_{width}px.png")
                            with open(out_p, "wb") as f:
                                f.write(base64.b64decode(shot["data"]))
                            print(f"Saved: {out_p} ({os.path.getsize(out_p)} bytes)")

            # 2. Capture Inner Pages at 1280px and 375px
            inner_pages_to_capture = [
                ("about-us", "inner_about_us"),
                ("permanent-hiring-solutions", "inner_permanent_hiring"),
                ("our-specialty", "inner_our_specialty"),
                ("job-seekers", "inner_job_seekers"),
                ("contact-us", "inner_contact_us")
            ]

            for path_segment, name in inner_pages_to_capture:
                url = f"http://localhost:3000/{path_segment}/index.html"
                await send_cmd("Page.navigate", {"url": url})
                await asyncio.sleep(1.0)
                await send_cmd("Runtime.evaluate", {
                    "expression": "document.documentElement.style.scrollBehavior = 'auto';"
                })

                for width in [1280, 375]:
                    height = 900 if width == 1280 else 812
                    await send_cmd("Emulation.setDeviceMetricsOverride", {
                        "width": width,
                        "height": height,
                        "deviceScaleFactor": 1,
                        "mobile": (width == 375)
                    })
                    await send_cmd("Emulation.setVisibleSize", {"width": width, "height": height})
                    await asyncio.sleep(0.3)

                    # Capture the full main content landmark (.page-content-section)
                    box = (await send_cmd("Runtime.evaluate", {
                        "expression": """
                        (() => {
                            const el = document.querySelector('.page-content-section');
                            if (!el) return null;
                            const r = el.getBoundingClientRect();
                            return { x: r.left + window.pageXOffset, y: r.top + window.pageYOffset, width: r.width, height: r.height };
                        })()
                        """,
                        "returnByValue": True
                    })).get("result", {}).get("value")

                    if box:
                        shot = await send_cmd("Page.captureScreenshot", {
                            "format": "png",
                            "clip": {
                                "x": float(box["x"]),
                                "y": float(box["y"]),
                                "width": float(box["width"]),
                                "height": float(box["height"]),
                                "scale": 1
                            },
                            "captureBeyondViewport": True
                        })
                        if shot.get("data"):
                            out_p = os.path.join(SCREENSHOTS_DIR, f"{name}_{width}px.png")
                            with open(out_p, "wb") as f:
                                f.write(base64.b64decode(shot["data"]))
                            print(f"Saved: {out_p} ({os.path.getsize(out_p)} bytes)")

            print(f"\nTotal console exceptions caught across all pages: {len(console_errors)}")
            if console_errors:
                print("Console errors:", console_errors)

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
        if os.path.exists(user_data):
            try:
                shutil.rmtree(user_data, ignore_errors=True)
            except Exception:
                pass

if __name__ == "__main__":
    asyncio.run(capture_all())
