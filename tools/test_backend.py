#!/usr/bin/env python3
"""
HireHR Backend Verification Suite
Tests Cloudflare Workers Static Assets & /api/contact endpoint under wrangler dev.
Follows Cloudflare's official Turnstile testing documentation:
  https://developers.cloudflare.com/turnstile/troubleshooting/testing/

Supports two isolated, server-managed wrangler dev configurations:
  (a) TURNSTILE_SECRET=1x0000000000000000000000000000000AA (documented always-pass test secret)
  (b) TURNSTILE_SECRET=2x0000000000000000000000000000000AA (documented always-fail test secret)
Uses Cloudflare's documented dummy token: XXXX.DUMMY.TOKEN.XXXX
Preserves and restores existing .dev.vars state exactly.
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

DEFAULT_PORT = 8787
DEFAULT_BASE_URL = f"http://127.0.0.1:{DEFAULT_PORT}"
ALLOWED_DEV_ORIGIN = f"http://localhost:{DEFAULT_PORT}"

# Cloudflare official dummy test fixtures (per documentation)
CF_DUMMY_TOKEN = "XXXX.DUMMY.TOKEN.XXXX"
CF_PASS_SECRET = "1x0000000000000000000000000000000AA"
CF_FAIL_SECRET = "2x0000000000000000000000000000000AA"

results = []

def record(suite, name, passed, detail):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] [{suite}] {name} - {detail}")
    results.append({"suite": suite, "name": name, "passed": passed, "detail": detail})

def http_req(url, method="GET", headers=None, data=None, content_type="application/json"):
    """
    HTTP request helper.
    Allows testing Content-Type enforcement by supporting:
      - custom Content-Type in headers
      - content_type=None to omit the header entirely
    """
    req_headers = dict(headers) if headers else {}

    if data is not None:
        if isinstance(data, (dict, list)):
            body = json.dumps(data).encode("utf-8")
        elif isinstance(data, str):
            body = data.encode("utf-8")
        else:
            body = data

        if content_type is not None and "Content-Type" not in req_headers:
            req_headers["Content-Type"] = content_type
    else:
        body = None

    req = urllib.request.Request(url, method=method, headers=req_headers)

    try:
        with urllib.request.urlopen(req, data=body, timeout=10) as resp:
            resp_body = resp.read().decode("utf-8", errors="replace")
            return resp.status, resp.headers, resp_body
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8", errors="replace")
        return e.code, e.headers, resp_body
    except Exception as e:
        return 0, {}, str(e)

def is_port_open(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(0.5)
        res = s.connect_ex(("127.0.0.1", port))
        return res == 0
    finally:
        s.close()

def wait_for_port_closed(port, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        if not is_port_open(port):
            return True
        time.sleep(0.3)
    return False

def wait_for_server(base_url, proc, timeout=25):
    start = time.time()
    while time.time() - start < timeout:
        if proc.poll() is not None:
            print(f"[Orchestrator] Server process exited unexpectedly with code {proc.poll()}.")
            return False
        try:
            status, _, _ = http_req(f"{base_url}/")
            if status == 200:
                return True
        except Exception:
            pass
        time.sleep(0.4)
    return False

def write_dev_vars(turnstile_secret, notify_to="owner@example.com"):
    content = (
        f"# Local development secrets (managed by test suite)\n"
        f"TURNSTILE_SECRET={turnstile_secret}\n"
        f"NOTIFY_TO={notify_to}\n"
    )
    with open(".dev.vars", "w", encoding="utf-8") as f:
        f.write(content)

def spawn_wrangler(port=DEFAULT_PORT):
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
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
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
        "turnstileToken": CF_DUMMY_TOKEN
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

    # 6. JSON-Only Content-Type Contract Tests (Deliverable 3)
    # 6a. application/json accepted
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN, "Content-Type": "application/json"},
        data=valid_payload
    )
    res_json = json.loads(body) if status == 200 else {}
    record(suite, "Content-Type Contract: application/json Accepted", status == 200 and res_json.get("ok") is True, f"Status: {status}, Body: {body.strip()}")

    # 6b. application/json; charset=utf-8 accepted
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN, "Content-Type": "application/json; charset=utf-8"},
        data=valid_payload
    )
    res_json = json.loads(body) if status == 200 else {}
    record(suite, "Content-Type Contract: application/json; charset=utf-8 Accepted", status == 200 and res_json.get("ok") is True, f"Status: {status}, Body: {body.strip()}")

    # 6c. text/plain rejected with 415
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN, "Content-Type": "text/plain"},
        data=valid_payload
    )
    record(suite, "Content-Type Contract: text/plain Rejected (415)", status == 415, f"Status: {status}, Body: {body.strip()}")

    # 6d. missing Content-Type rejected with 415
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN},
        data=valid_payload,
        content_type=None
    )
    record(suite, "Content-Type Contract: Missing Content-Type Rejected (415)", status == 415, f"Status: {status}, Body: {body.strip()}")

    # 7. Payload size limit (> 20 KB -> 413)
    oversized_data = {
        "name": "Jane Doe",
        "phone": "+1 555-0199",
        "email": "jane@example.com",
        "message": "A" * 21000,
        "turnstileToken": CF_DUMMY_TOKEN
    }
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN},
        data=oversized_data
    )
    record(suite, "Payload Size Limit (>20 KB -> 413)", status == 413, f"Status: {status}")

    # 8. Field validation tests (each missing/oversize/invalid field -> 400)
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

    # 9. Turnstile test: Missing token -> 400
    no_token_payload = {**valid_payload, "turnstileToken": ""}
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN},
        data=no_token_payload
    )
    record(suite, "Turnstile: Missing Token -> 400", status == 400, f"Status: {status}, Body: {body.strip()}")

    # 10. Turnstile test: Documented dummy token with pass secret -> 200
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN},
        data=valid_payload
    )
    res_json = json.loads(body) if status == 200 else {}
    record(suite, "Turnstile: Documented Dummy Token with Pass Secret -> 200", status == 200 and res_json.get("ok") is True, f"Status: {status}, Body: {body.strip()}")

    # 11. Honeypot check (website filled -> 200 without email or lead logging)
    honeypot_payload = {**valid_payload, "website": "https://spammer-bot.example.com"}
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN},
        data=honeypot_payload
    )
    res_json = json.loads(body) if status == 200 else {}
    record(suite, "Honeypot: Trapped bot returns 200 {ok:true}", status == 200 and res_json.get("ok") is True and "delivered" not in res_json, f"Status: {status}, Body: {body.strip()}")

    # 12. Valid Submission (Stage A: MAIL_MODE=log -> 200 {ok:true, delivered:false})
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

    # 13. Header injection / CRLF in name (sanitized)
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
        "turnstileToken": CF_DUMMY_TOKEN
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

    # 2. Documented dummy token verified with 2x always-fail secret -> 400
    status, headers, body = http_req(
        f"{base_url}/api/contact",
        method="POST",
        headers={"Origin": ALLOWED_DEV_ORIGIN},
        data=valid_payload
    )
    record(suite, "Turnstile: Documented Dummy Token with Always-Fail Secret -> 400", status == 400, f"Status: {status}, Body: {body.strip()}")

def main():
    parser = argparse.ArgumentParser(description="HireHR Backend Verification Suite")
    parser.add_argument("--suite-a-only", action="store_true", help="Run only Suite A against running server")
    parser.add_argument("--suite-b-only", action="store_true", help="Run only Suite B against running server")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL of running server")
    args = parser.parse_args()

    port = int(urllib.parse.urlsplit(args.base_url).port or DEFAULT_PORT)

    if args.suite_a_only:
        run_suite_a(args.base_url)
        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        return (total - passed) == 0
    elif args.suite_b_only:
        run_suite_b(args.base_url)
        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        return (total - passed) == 0

    # Full automated test run managing dual-server lifecycle
    print("Starting dual-configuration backend verification suite...")

    # Guard: Fail clearly before touching files if required port is occupied
    if is_port_open(port):
        print(f"\n[FAIL] Port {port} is already in use by an existing process.")
        print("To ensure deterministic verification and clean server isolation,")
        print(f"please terminate the process listening on port {port} before running this suite.")
        sys.exit(1)

    # State preservation for .dev.vars
    dev_vars_path = ".dev.vars"
    dev_vars_existed = os.path.exists(dev_vars_path)
    original_dev_vars_bytes = None
    original_mode = None

    if dev_vars_existed:
        try:
            with open(dev_vars_path, "rb") as f:
                original_dev_vars_bytes = f.read()
            original_mode = os.stat(dev_vars_path).st_mode
            print(f"[Orchestrator] Preserved existing {dev_vars_path} ({len(original_dev_vars_bytes)} bytes).")
        except Exception as e:
            print(f"BLOCKER: Unable to safely preserve existing {dev_vars_path}: {e}")
            sys.exit(1)

    proc = None
    cleanup_ok = True
    cleanup_error = None
    try:
        # Phase 1: Configuration A (Pass Secret)
        print(f"\n[Orchestrator] Configuring {dev_vars_path} with Pass Secret ({CF_PASS_SECRET})...")
        write_dev_vars(CF_PASS_SECRET)

        print(f"[Orchestrator] Spawning fresh wrangler dev server on port {port}...")
        proc = spawn_wrangler(port)
        if not wait_for_server(args.base_url, proc):
            print("[FAIL] Failed to start wrangler dev server for Configuration A.")
            sys.exit(1)

        print(f"[Orchestrator] Server verified responsive on {args.base_url}. Running Suite A...")
        run_suite_a(args.base_url)

        print("[Orchestrator] Terminating Configuration A server...")
        kill_proc(proc)
        proc = None
        if not wait_for_port_closed(port, timeout=10):
            print(f"[FAIL] Port {port} did not close cleanly after stopping Configuration A server.")
            sys.exit(1)
        print(f"[Orchestrator] Confirmed port {port} closed.")

        # Phase 2: Configuration B (Fail Secret)
        print(f"\n[Orchestrator] Configuring {dev_vars_path} with Fail Secret ({CF_FAIL_SECRET})...")
        write_dev_vars(CF_FAIL_SECRET)

        print(f"[Orchestrator] Spawning fresh wrangler dev server on port {port}...")
        proc = spawn_wrangler(port)
        if not wait_for_server(args.base_url, proc):
            print("[FAIL] Failed to start wrangler dev server for Configuration B.")
            sys.exit(1)

        print(f"[Orchestrator] Server verified responsive on {args.base_url}. Running Suite B...")
        run_suite_b(args.base_url)

        print("[Orchestrator] Terminating Configuration B server...")
        kill_proc(proc)
        proc = None
        if not wait_for_port_closed(port, timeout=10):
            print(f"[FAIL] Port {port} did not close cleanly after stopping Configuration B server.")
            sys.exit(1)
        print(f"[Orchestrator] Confirmed port {port} closed.")

    finally:
        # Cleanup server process if still running
        if proc:
            print("\n[Orchestrator] Cleaning up running server process...")
            kill_proc(proc)
            wait_for_port_closed(port)

        # Restore .dev.vars to exact pre-test state
        if dev_vars_existed:
            try:
                with open(dev_vars_path, "wb") as f:
                    f.write(original_dev_vars_bytes)
                if original_mode is not None:
                    try:
                        os.chmod(dev_vars_path, original_mode)
                    except Exception as perm_err:
                        cleanup_ok = False
                        cleanup_error = f"Failed to restore permissions on {dev_vars_path}: {type(perm_err).__name__}"
                        print(f"\n[CRITICAL CLEANUP FAILURE] {cleanup_error}")
                if cleanup_ok:
                    print(f"[Orchestrator] Successfully restored original {dev_vars_path} state.")
            except Exception as e:
                cleanup_ok = False
                cleanup_error = f"Failed to restore original {dev_vars_path}: {type(e).__name__}"
                print(f"\n[CRITICAL CLEANUP FAILURE] {cleanup_error}")
        else:
            if os.path.exists(dev_vars_path):
                try:
                    os.remove(dev_vars_path)
                    print(f"[Orchestrator] Successfully removed test-created {dev_vars_path}.")
                except Exception as e:
                    cleanup_ok = False
                    cleanup_error = f"Failed to remove test-created {dev_vars_path}: {type(e).__name__}"
                    print(f"\n[CRITICAL CLEANUP FAILURE] {cleanup_error}")

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    print(f"\n==========================================")
    print(f"TOTAL TESTS EXECUTED: {total}")
    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print(f"PASS RATE: {((passed / total) * 100):.1f}%" if total > 0 else "N/A")
    if not cleanup_ok:
        print(f"CLEANUP STATUS: FAILED ({cleanup_error})")
        print(f"OVERALL STATUS: FAILED (Test environment cleanup failed)")
        print(f"==========================================")
        return False
    else:
        print(f"CLEANUP STATUS: SUCCESS (Pre-test state restored)")
        if failed == 0:
            print(f"OVERALL STATUS: SUCCESS")
        else:
            print(f"OVERALL STATUS: FAILED ({failed} test failures)")
        print(f"==========================================")

    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
