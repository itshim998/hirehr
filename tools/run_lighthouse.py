import subprocess
import time
import http.server
import socketserver
import threading
import json
import os

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def run():
    port = 8089
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), QuietHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    print(f"Server started on port {port}")

    targets = [
        ("home", f"http://127.0.0.1:{port}/index.html", "docs/lighthouse_home.json"),
        ("about", f"http://127.0.0.1:{port}/about-us/index.html", "docs/lighthouse_about.json")
    ]

    results = {}

    try:
        for name, url, out_path in targets:
            print(f"Running Lighthouse for {name} ({url})...")
            cmd = [
                "npx.cmd",
                "lighthouse",
                url,
                "--output=json",
                f"--output-path={out_path}",
                "--chrome-flags=--headless=new --no-sandbox --disable-gpu",
                "--only-categories=performance,accessibility,best-practices,seo",
                "--form-factor=mobile",
                "--throttling.rttMs=40",
                "--throttling.throughputKbps=10240",
                "--throttling.cpuSlowdownMultiplier=1",
                "--quiet"
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if os.path.exists(out_path):
                with open(out_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cats = data.get("categories", {})
                scores = {
                    "performance": int((cats.get("performance", {}).get("score") or 0) * 100),
                    "accessibility": int((cats.get("accessibility", {}).get("score") or 0) * 100),
                    "best-practices": int((cats.get("best-practices", {}).get("score") or 0) * 100),
                    "seo": int((cats.get("seo", {}).get("score") or 0) * 100)
                }
                results[name] = scores
                print(f"  {name} scores: {scores}")
            else:
                print(f"  Failed for {name}: {res.stderr}")
    finally:
        server.shutdown()

    with open("docs/lighthouse_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("Lighthouse run complete.")

if __name__ == "__main__":
    run()
