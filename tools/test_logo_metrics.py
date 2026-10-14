import asyncio, json, urllib.request, subprocess, time, websockets, os, shutil

async def test_logo():
    port = 9224
    user_data = os.path.abspath("tmp_chrome_logo")
    proc = subprocess.Popen([
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "--headless=new",
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data}",
        "--disable-gpu",
        "--no-first-run"
    ])
    time.sleep(2)
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/json/new?http://localhost:3000/index.html", method="PUT")
        with urllib.request.urlopen(req) as resp:
            ws_url = json.loads(resp.read().decode())["webSocketDebuggerUrl"]
        async with websockets.connect(ws_url) as ws:
            msg_id = 0
            async def send(method, params=None):
                nonlocal msg_id
                msg_id += 1
                await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
                while True:
                    r = json.loads(await ws.recv())
                    if r.get("id") == msg_id:
                        return r.get("result", {})
            await send("Runtime.enable")
            await send("Page.enable")
            await asyncio.sleep(1)
            
            # Check 1280px
            await send("Emulation.setDeviceMetricsOverride", {"width": 1280, "height": 800, "deviceScaleFactor": 1, "mobile": False})
            await asyncio.sleep(0.3)
            h_eval = await send("Runtime.evaluate", {
                "expression": "document.querySelector('.nav-bar').getBoundingClientRect().height"
            })
            nav_height = h_eval["result"]["value"]
            print(f"Desktop (1280px) nav bar height: {nav_height:.1f}px")
            
            # Check 320px
            await send("Emulation.setDeviceMetricsOverride", {"width": 320, "height": 568, "deviceScaleFactor": 2, "mobile": True})
            await asyncio.sleep(0.3)
            scroll_eval = await send("Runtime.evaluate", {
                "expression": "document.documentElement.scrollWidth > document.documentElement.clientWidth"
            })
            has_scroll = scroll_eval["result"]["value"]
            print(f"Mobile (320px) horizontal scroll: {has_scroll}")
            
            # Check wordmark text + logo fit
            brand_eval = await send("Runtime.evaluate", {
                "expression": """
                (() => {
                    const b = document.querySelector('.brand-wordmark').getBoundingClientRect();
                    const btn = document.querySelector('.nav-toggle').getBoundingClientRect();
                    return { brandRight: b.right, btnLeft: btn.left, overlap: b.right > btn.left };
                })()
                """,
                "returnByValue": True
            })
            print("Mobile 320px brand/button metrics:", brand_eval["result"]["value"])
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
        if os.path.exists(user_data):
            shutil.rmtree(user_data, ignore_errors=True)

if __name__ == "__main__":
    asyncio.run(test_logo())
