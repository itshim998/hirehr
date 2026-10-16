import asyncio, json, urllib.request, subprocess, time, websockets, os, shutil

async def check_console():
    port = 9223
    user_data = os.path.abspath("tmp_chrome_console")
    proc = subprocess.Popen([
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        '--headless=new',
        f'--remote-debugging-port={port}',
        f'--user-data-dir={user_data}',
        '--disable-gpu',
        '--no-first-run'
    ])
    time.sleep(2)
    errors = []
    try:
        req = urllib.request.Request(f'http://127.0.0.1:{port}/json/new?http://localhost:3000/index.html', method='PUT')
        with urllib.request.urlopen(req) as resp:
            ws_url = json.loads(resp.read().decode())['webSocketDebuggerUrl']
        async with websockets.connect(ws_url) as ws:
            msg_id = 0
            async def send(method, params=None):
                nonlocal msg_id
                msg_id += 1
                await ws.send(json.dumps({'id': msg_id, 'method': method, 'params': params or {}}))
                while True:
                    r = json.loads(await ws.recv())
                    if r.get('method') == 'Runtime.exceptionThrown':
                        errors.append(r)
                    if r.get('id') == msg_id:
                        return r.get('result', {})
            await send('Runtime.enable')
            await send('Page.enable')
            await asyncio.sleep(1.5)
            # Cycle through all slides
            for i in range(5):
                js_code = f"document.querySelectorAll('.slider-dot')[{i}].click()"
                await send('Runtime.evaluate', {'expression': js_code})
                await asyncio.sleep(0.5)
        print('Console exceptions count:', len(errors))
        if errors:
            print('Errors:', errors)
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

if __name__ == '__main__':
    asyncio.run(check_console())
