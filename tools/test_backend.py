#!/usr/bin/env python3
"""
HireHR Backend Verification Suite
Tests Cloudflare Workers Static Assets & /api/contact endpoint under wrangler dev
"""

import urllib.request
import urllib.error
import urllib.parse
import json
import sys

BASE_URL = "http://127.0.0.1:8787"
ORIGIN = "http://localhost:8787"
ALWAYS_PASS_TOKEN = "1x00000000000000000000AA"
ALWAYS_FAIL_TOKEN = "2x00000000000000000000AB"

results = []

def record(name, passed, detail):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name} - {detail}")
    results.append({"name": name, "passed": passed, "detail": detail})

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

def run_tests():
    print(f"Running backend verification tests against {BASE_URL}...\n")

    # 1. Static asset serving
    status, headers, body = http_req(f"{BASE_URL}/")
    record("Static Homepage (/)", status == 200 and "HireHR" in body, f"Status: {status}")

    status, headers, body = http_req(f"{BASE_URL}/about-us/")
    record("Static Inner Page (/about-us/)", status == 200 and "About Us" in body, f"Status: {status}")

    status, headers, body = http_req(f"{BASE_URL}/css/style.css")
    record("Static Asset (/css/style.css)", status == 200 and "--color-primary" in body, f"Status: {status}")

    status, headers, body = http_req(f"{BASE_URL}/js/main.js")
    record("Static Asset (/js/main.js)", status == 200 and "FORM_ENDPOINT" in body, f"Status: {status}")

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
        status, headers, body = http_req(f"{BASE_URL}{path}")
        record(f"Excluded Asset Hidden ({path})", status == 404, f"Returned status: {status}")

    # 3. Security headers on static responses
    status, headers, _ = http_req(f"{BASE_URL}/")
    has_nosniff = headers.get("X-Content-Type-Options") == "nosniff"
    has_referrer = headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    has_frame = headers.get("X-Frame-Options") == "DENY"
    has_csp = "https://challenges.cloudflare.com" in (headers.get("Content-Security-Policy") or "")
    record("Security Header: X-Content-Type-Options", has_nosniff, f"Value: {headers.get('X-Content-Type-Options')}")
    record("Security Header: Referrer-Policy", has_referrer, f"Value: {headers.get('Referrer-Policy')}")
    record("Security Header: X-Frame-Options", has_frame, f"Value: {headers.get('X-Frame-Options')}")
    record("Security Header: Content-Security-Policy", has_csp, f"Value: {headers.get('Content-Security-Policy')}")

    # 4. Method not allowed (GET /api/contact -> 405)
    status, headers, body = http_req(f"{BASE_URL}/api/contact", method="GET")
    record("HTTP Method Check (GET -> 405)", status == 405 and headers.get("Allow") == "POST", f"Status: {status}, Allow: {headers.get('Allow')}")

    # 5. Wrong Origin check (POST /api/contact with wrong Origin -> 403)
    valid_payload = {
        "name": "Jane Doe",
        "company": "Acme Corp",
        "phone": "+1 555-0199",
        "email": "jane@example.com",
        "message": "Looking for permanent hiring solutions.",
        "turnstileToken": ALWAYS_PASS_TOKEN
    }
    status, headers, body = http_req(
        f"{BASE_URL}/api/contact",
        method="POST",
        headers={"Origin": "https://malicious-site.example.com"},
        data=valid_payload
    )
    record("Cross-Site Origin Rejection (Wrong Origin -> 403)", status == 403, f"Status: {status}, Body: {body.strip()}")

    # 6. Payload size limit (> 20 KB -> 413)
    oversized_data = {
        "name": "Jane Doe",
        "phone": "+1 555-0199",
        "email": "jane@example.com",
        "message": "A" * 21000,
        "turnstileToken": ALWAYS_PASS_TOKEN
    }
    status, headers, body = http_req(
        f"{BASE_URL}/api/contact",
        method="POST",
        headers={"Origin": ORIGIN},
        data=oversized_data
    )
    record("Payload Size Limit (>20 KB -> 413)", status == 413, f"Status: {status}")

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
            f"{BASE_URL}/api/contact",
            method="POST",
            headers={"Origin": ORIGIN},
            data=test_payload
        )
        record(f"Validation: {test_label} -> 400", status == 400, f"Status: {status}, Body: {body.strip()}")

    # 8. Turnstile verification tests
    # Missing token -> 400
    no_token_payload = {**valid_payload, "turnstileToken": ""}
    status, headers, body = http_req(
        f"{BASE_URL}/api/contact",
        method="POST",
        headers={"Origin": ORIGIN},
        data=no_token_payload
    )
    record("Turnstile: Missing Token -> 400", status == 400, f"Status: {status}, Body: {body.strip()}")

    # Invalid token (Cloudflare always-fail test secret / token) -> 400
    invalid_token_payload = {**valid_payload, "turnstileToken": ALWAYS_FAIL_TOKEN}
    status, headers, body = http_req(
        f"{BASE_URL}/api/contact",
        method="POST",
        headers={"Origin": ORIGIN},
        data=invalid_token_payload
    )
    record("Turnstile: Invalid Token -> 400", status == 400, f"Status: {status}, Body: {body.strip()}")

    # 9. Honeypot check (website filled -> 200 without email or lead logging)
    honeypot_payload = {**valid_payload, "website": "https://spammer-bot.example.com"}
    status, headers, body = http_req(
        f"{BASE_URL}/api/contact",
        method="POST",
        headers={"Origin": ORIGIN},
        data=honeypot_payload
    )
    res_json = json.loads(body) if status == 200 else {}
    record("Honeypot: Trapped bot returns 200 {ok:true}", status == 200 and res_json.get("ok") is True and "delivered" not in res_json, f"Status: {status}, Body: {body.strip()}")

    # 10. Valid Submission (Stage A: MAIL_MODE=log -> 200 {ok:true, delivered:false})
    status, headers, body = http_req(
        f"{BASE_URL}/api/contact",
        method="POST",
        headers={"Origin": ORIGIN},
        data=valid_payload
    )
    res_json = json.loads(body) if status == 200 else {}
    has_no_store = "no-store" in (headers.get("Cache-Control") or "")
    is_valid_success = status == 200 and res_json.get("ok") is True and res_json.get("delivered") is False and has_no_store
    record("Valid Submission (Stage A MAIL_MODE=log)", is_valid_success, f"Status: {status}, Body: {body.strip()}, Cache-Control: {headers.get('Cache-Control')}")

    # 11. Header injection / CRLF in name (sanitized)
    crlf_name_payload = {**valid_payload, "name": "Jane\r\nDoe\r\nSubject: Injected"}
    status, headers, body = http_req(
        f"{BASE_URL}/api/contact",
        method="POST",
        headers={"Origin": ORIGIN},
        data=crlf_name_payload
    )
    res_json = json.loads(body) if status == 200 else {}
    record("Header Injection: CRLF sanitized in name", status == 200 and res_json.get("ok") is True, f"Status: {status}, Body: {body.strip()}")

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    print(f"\n==========================================")
    print(f"TESTS COMPLETE: {passed}/{total} passed ({failed} failed)")
    print(f"==========================================")
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
