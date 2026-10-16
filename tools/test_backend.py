#!/usr/bin/env python3
"""
HireHR Backend Verification Suite
Tests Cloudflare Workers Static Assets & /api/contact endpoint under wrangler dev.
Supports running against two wrangler dev configurations:
  (a) TURNSTILE_SECRET=1x0000000000000000000000000000000AA (always-pass test secret)
  (b) TURNSTILE_SECRET=2x0000000000000000000000000000000AA (always-fail test secret)
"""

import urllib.request
import urllib.error
import urllib.parse
import json
import sys
import os
import time
import subprocess
import socket
import argparse

DEFAULT_BASE_URL = "http://127.0.0.1:8787"
ALLOWED_DEV_ORIGIN = "http://localhost:8787"
REALISTIC_PASS_TOKEN = "0.test-realistic-turnstile-token-sample-string-12345"
REALISTIC_FAIL_TOKEN = "0.test-realistic-turnstile-token-sample-string-67890"

SECRET_PASS = "1x0000000000000000000000000000000AA"
SECRET_FAIL = "2x0000000000000000000000000000000AA"

results = []

def record(suite, name, passed, detail):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] [{suite}] {name} - {detail}")
    results.append({"suite": suite, "name": name, "passed": passed, "detail": detail})

def http_req(url, method="GET", headers=None, data=None):
    if headers is None:
        headers = {}
    req = urllib.request.Request(url, method=method, headers=headers)
    if data is not None:
        if isinstance(data, (dict, list)):
            body = json.dumps(data).encode("utf-8")
            if "Content-Type" not in headers:
                req.add_header("Content-Type", "application/json")
        elif isinstance(data, str):
            body = data.encode("utf-8")
        else:
            body = data
    else:
        body = None

    try:
        with urllib.request.urlopen(req, data=body, timeout=10) as resp:
            resp_body = resp.read().decode("utf-8", errors="replace")
            return resp.status, resp.headers, resp_body
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8", errors="replace")
        return e.code, e.headers, resp_body
    except Exception as e:
        return 0, {}, str(e)

def wait_for_server(base_url, timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        try:
            status, _, _ = http_req(f"{base_url}/")
            if status == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

def is_port_open(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(0.5)
        res = s.connect_ex(("127.0.0.1", port))
        return res == 0
    finally:
        s.close()

def write_dev_vars(turnstile_secret, notify_to="owner@example.com"):
    content = (
        f"# Local development secrets\n"
        f"TURNSTILE_SECRET={turnstile_secret}\n"
        f"NOTIFY_TO={notify_to}\n"
    )
    with open(".dev.vars", "w", encoding="utf-8") as f:
        f.write(content)

def spawn_wrangler(port=8787):
    is_windows = os.name == "nt"
    cmd = ["npx.cmd" if is_windows else "npx", "wrangler", "dev", "--port", str(port)]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return proc

def kill_proc(proc):
    if not proc:
        return
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            proc.terminate()
            proc.wait(timeout=5)
    except Exception:
        pass

def run_suite_a(base_url):
    suite = "Config A (Pass Secret)"
    print(f"\n--- Running {suite} against {base_url} ---")

    # 1. Static asset serving
    status, headers, body = http_req(f"{base_url}/")
    record(suite, "Static Homepage (/)", status == 200 and "HireHR" in body, f"Status: {status}")

    status, headers, body = http_req(f"{base_url}/about-us/")
    record(suite, "Static Inner Page (/about-us/)", status == 200 and "About Us" in body, f"Status: {status}")

    status, headers, body = http_req(f"{base_url}/css/style.css")
    record(suite, "Static Asset (/css/style.css)", status == 200 and "--color-primary" in body, f"Status: {status}")

    status, headers, body = http_req(f"{base_url}/js/main.js")
    record(suite, "Static Asset (/js/main.js)", status == 200 and "FORM_ENDPOINT" in body, f"Status: {status}")

    # 2. Excluded paths from .assetsignore must return 404
    for path in [
        "/original/",
        "/original/index.original.html",
        "/docs/",
        "/docs/REPORT.md",
        "/tools/",
        "/tools/verify_site.py",
        "/prompt.txt",
        "/worker/index.js",
        "/wrangler.jsonc",
        "/content/pages.json",
        "/.dev.vars",
        "/.dev.vars.example"
    ]:
        status, headers, body = http_req(f"{base_url}{path}")
        record(suite, f"Excluded Asset Hidden ({path})", status == 404, f"Returned status: {status}")

    # 3. Security headers on static responses
    status, headers, _ = http_req(f"{base_url}/")
    has_nosniff = headers.get("X-Content-Type-Options") == "nosniff"
    has_referrer = headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    has_frame = headers.get("X-Frame-Options") == "DENY"
    has_csp = "https://challenges.cloudflare.com" in (headers.get("Content-Security-Policy") or "")
    record(suite, "Security Header: X-Content-Type-Options", has_nosniff, f"Value: {headers.get('X-Content-Type-Options')}")
    record(suite, "Security Header: Referrer-Policy", has_referrer, f"Value: {headers.get('Referrer-Policy')}")
    record(suite, "Security Header: X-Frame-Options", has_frame, f"Value: {headers.get('X-Frame-Options')}")
    record(suite, "Security Header: Content-Security-Policy", has_csp, f"Value: {headers.get('Content-Security-Policy')}")

    # 4. Method not allowed (GET /api/contact -> 405)
    status, headers, body = http_req(f"{base_url}/api/contact", method="GET")
    record(suite, "HTTP Method Check (GET -> 405)", status == 405 and headers.get("Allow") == "POST", f"Status: {status}, Allow: {headers.get('Allow')}")

    valid_payload = {
        "name": "Jane Doe",
        "company": "Acme Corp",
        "phone": "+1 555-0199",
        "email": "jane@example.com",
        "message": "Looking for permanent hiring solutions.",
        "turnstileToken": REALISTIC_PASS_TOKEN
    }

    # 5. Strict Origin Policy Tests (OPTIONS and POST)
    # 5a. POST with no Origin and no Sec-Fetch-Site -> 403
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={},
        data=valid_payload
    )
    record(suite, "Origin Policy: No Origin & No Sec-Fetch-Site -> 403", status == 403, f"Status: {status}, Body: {body.strip()}")

    # 5b. POST with wrong Origin -> 403
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": "https://malicious-site.example.com"},
        data=valid_payload
    )
    record(suite, "Origin Policy: Wrong Cross-Site Origin -> 403", status == 403, f"Status: {status}, Body: {body.strip()}")

    # 5c. OPTIONS with wrong Origin -> 403
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="OPTIONS",
        headers={"Origin": "https://malicious-site.example.com"}
    )
    record(suite, "Origin Policy: OPTIONS Preflight Wrong Origin -> 403", status == 403, f"Status: {status}")

    # 5d. OPTIONS with allowed Origin -> 204
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="OPTIONS",
        headers={"Origin": ALLOWED_DEV_ORIGIN}
    )
    record(suite, "Origin Policy: OPTIONS Preflight Allowed Origin -> 204", status == 204 and headers.get("Access-Control-Allow-Origin") == ALLOWED_DEV_ORIGIN, f"Status: {status}, ACAO: {headers.get('Access-Control-Allow-Origin')}")

    # 5e. POST with no Origin but Sec-Fetch-Site: same-origin -> passes origin stage
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Sec-Fetch-Site": "same-origin"},
        data=valid_payload
    )
    res_json = json.loads(body) if status == 200 else {}
    record(suite, "Origin Policy: No Origin with Sec-Fetch-Site same-origin -> Passes Origin (200)", status == 200 and res_json.get("ok") is True, f"Status: {status}, Body: {body.strip()}")

    # 5f. POST with request URL's own origin (http://127.0.0.1:8787) -> passes origin stage
    req_own_origin = urllib.parse.urlsplit(base_url).scheme + "://" + urllib.parse.urlsplit(base_url).netloc
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": req_own_origin},
        data=valid_payload
    )
    res_json = json.loads(body) if status == 200 else {}
    record(suite, "Origin Policy: Request URL Own Origin -> Passes Origin (200)", status == 200 and res_json.get("ok") is True, f"Status: {status}, Body: {body.strip()}")

    # 5g. POST with ALLOWED_ORIGINS origin (http://localhost:8787) -> passes origin stage
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN},
        data=valid_payload
    )
    res_json = json.loads(body) if status == 200 else {}
    record(suite, "Origin Policy: ALLOWED_ORIGINS Header -> Passes Origin (200)", status == 200 and res_json.get("ok") is True, f"Status: {status}, Body: {body.strip()}")

    # 6. Payload size limit (> 20 KB -> 413)
    oversized_data = {
        "name": "Jane Doe",
        "phone": "+1 555-0199",
        "email": "jane@example.com",
        "message": "A" * 21000,
        "turnstileToken": REALISTIC_PASS_TOKEN
    }
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN},
        data=oversized_data
    )
    record(suite, "Payload Size Limit (>20 KB -> 413)", status == 413, f"Status: {status}")

    # 7. Field validation tests (each missing/oversize/invalid field -> 400)
    validation_cases = [
        ("Missing Name", {**valid_payload, "name": ""}),
        ("Oversize Name (>100)", {**valid_payload, "name": "A" * 101}),
        ("Oversize Company (>150)", {**valid_payload, "company": "B" * 151}),
        ("Missing Phone", {**valid_payload, "phone": ""}),
        ("Oversize Phone (>30)", {**valid_payload, "phone": "+1 " + "9" * 30}),
        ("Invalid Phone Characters", {**valid_payload, "phone": "123-abc-4567"}),
        ("Missing Email", {**valid_payload, "email": ""}),
        ("Invalid Email Format", {**valid_payload, "email": "not-an-email"}),
        ("Oversize Email (>254)", {**valid_payload, "email": "a" * 250 + "@test.com"}),
        ("CRLF in Email", {**valid_payload, "email": "user@example.com\r\nBcc: evil@example.com"}),
        ("Missing Message", {**valid_payload, "message": ""}),
        ("Oversize Message (>5000)", {**valid_payload, "message": "M" * 5001}),
        ("Unknown Field", {**valid_payload, "unexpectedField": "illegal"}),
    ]

    for test_label, test_payload in validation_cases:
        status, headers, body = http_req(
            f"{base_url}/api/contact",
            method="POST",
            headers={"Origin": ALLOWED_DEV_ORIGIN},
            data=test_payload
        )
        record(suite, f"Validation: {test_label} -> 400", status == 400, f"Status: {status}, Body: {body.strip()}")

    # 8. Turnstile test: Missing token -> 400
    no_token_payload = {**valid_payload, "turnstileToken": ""}
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN},
        data=no_token_payload
    )
    record(suite, "Turnstile: Missing Token -> 400", status == 400, f"Status: {status}, Body: {body.strip()}")

    # 9. Honeypot check (website filled -> 200 without email or lead logging)
    honeypot_payload = {**valid_payload, "website": "https://spammer-bot.example.com"}
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN},
        data=honeypot_payload
    )
    res_json = json.loads(body) if status == 200 else {}
    record(suite, "Honeypot: Trapped bot returns 200 {ok:true}", status == 200 and res_json.get("ok") is True and "delivered" not in res_json, f"Status: {status}, Body: {body.strip()}")

    # 10. Valid Submission (Stage A: MAIL_MODE=log -> 200 {ok:true, delivered:false})
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN},
        data=valid_payload
    )
    res_json = json.loads(body) if status == 200 else {}
    has_no_store = "no-store" in (headers.get("Cache-Control") or "")
    is_valid_success = status == 200 and res_json.get("ok") is True and res_json.get("delivered") is False and has_no_store
    record(suite, "Valid Submission (Stage A MAIL_MODE=log)", is_valid_success, f"Status: {status}, Body: {body.strip()}, Cache-Control: {headers.get('Cache-Control')}")

    # 11. Header injection / CRLF in name (sanitized)
    crlf_name_payload = {**valid_payload, "name": "Jane\r\nDoe\r\nSubject: Injected"}
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN},
        data=crlf_name_payload
    )
    res_json = json.loads(body) if status == 200 else {}
    record(suite, "Header Injection: CRLF sanitized in name", status == 200 and res_json.get("ok") is True, f"Status: {status}, Body: {body.strip()}")

def run_suite_b(base_url):
    suite = "Config B (Fail Secret)"
    print(f"\n--- Running {suite} against {base_url} ---")

    valid_payload = {
        "name": "Jane Doe",
        "company": "Acme Corp",
        "phone": "+1 555-0199",
        "email": "jane@example.com",
        "message": "Looking for permanent hiring solutions.",
        "turnstileToken": REALISTIC_FAIL_TOKEN
    }

    # 1. Missing token -> 400
    no_token_payload = {**valid_payload, "turnstileToken": ""}
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN},
        data=no_token_payload
    )
    record(suite, "Turnstile: Missing Token -> 400", status == 400, f"Status: {status}, Body: {body.strip()}")

    # 2. Invalid token / verification failure with 2x secret -> 400
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN},
        data=valid_payload
    )
    record(suite, "Turnstile: Invalid Token (Always-Fail Secret) -> 400", status == 400, f"Status: {status}, Body: {body.strip()}")

def main():
    parser = argparse.ArgumentParser(description="HireHR Backend Verification Suite")
    parser.add_argument("--suite-a-only", action="store_true", help="Run only Suite A against running server")
    parser.add_argument("--suite-b-only", action="store_true", help="Run only Suite B against running server")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL of running server")
    args = parser.parse_args()

    port = int(urllib.parse.urlsplit(args.base_url).port or 8787)

    if args.suite_a_only:
        run_suite_a(args.base_url)
    elif args.suite_b_only:
        run_suite_b(args.base_url)
    else:
        # Full automated run covering both wrangler dev configurations
        print("Starting dual-configuration backend verification suite...")

        # If a server is already on port 8787, we run Suite A, then restart with Config B, then restore Config A
        proc = None
        try:
            # 1. Setup Configuration A
            print(f"\n[Orchestrator] Setting up Configuration A (Pass Secret: {SECRET_PASS})...")
            write_dev_vars(SECRET_PASS)
            if not is_port_open(port):
                proc = spawn_wrangler(port)
                if not wait_for_server(args.base_url):
                    print("Failed to start wrangler dev for Configuration A.")
                    sys.exit(1)
            else:
                print(f"[Orchestrator] Using already running server on port {port} for Suite A.")

            run_suite_a(args.base_url)

            # Shut down server A if spawned
            if proc:
                print("[Orchestrator] Stopping Configuration A server...")
                kill_proc(proc)
                proc = None
                time.sleep(2)

            # 2. Setup Configuration B
            print(f"\n[Orchestrator] Setting up Configuration B (Fail Secret: {SECRET_FAIL})...")
            write_dev_vars(SECRET_FAIL)
            proc = spawn_wrangler(port)
            if not wait_for_server(args.base_url):
                print("Failed to start wrangler dev for Configuration B.")
                sys.exit(1)

            run_suite_b(args.base_url)

        finally:
            if proc:
                print("\n[Orchestrator] Stopping Configuration B server...")
                kill_proc(proc)
                time.sleep(1)
            # Restore default Configuration A .dev.vars
            write_dev_vars(SECRET_PASS)
            print("[Orchestrator] Restored .dev.vars to default (Config A Pass Secret).")

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    print(f"\n==========================================")
    print(f"TOTAL TESTS EXECUTED: {total}")
    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print(f"PASS RATE: {((passed / total) * 100):.1f}%" if total > 0 else "N/A")
    print(f"==========================================")

    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
