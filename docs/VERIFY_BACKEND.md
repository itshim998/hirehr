# Backend Verification Suite Report (`docs/VERIFY_BACKEND.md`)

Verification conducted for **HireHR Cloudflare Worker Backend (Stage A)** on branch `feature/contact-worker`.

Server runtime: `wrangler dev` (Wrangler v4.151.0 on Node v22.19.0).  
Target endpoint: `http://127.0.0.1:8787/api/contact`  
Static asset target: `http://127.0.0.1:8787/`

---

## 1. Automated API & Security Verification Suite (`tools/test_backend.py`)

53 of 53 automated checks passed (100% pass rate) across two distinct, server-managed `wrangler dev` configurations using Cloudflare's official documented testing fixtures (`XXXX.DUMMY.TOKEN.XXXX`) and production Turnstile verification.

### Configuration A: Cloudflare Documented Always-Pass Test Secret (`TURNSTILE_SECRET=1x0000000000000000000000000000000AA`)

#### A. Static Asset Serving & Routing
- [PASS] `GET /` -> HTTP 200 (serves static homepage `index.html`)
- [PASS] `GET /about-us/` -> HTTP 200 (serves static inner page `about-us/index.html` with auto-trailing-slash)
- [PASS] `GET /css/style.css` -> HTTP 200 (serves static CSS bundle)
- [PASS] `GET /js/main.js` -> HTTP 200 (serves static JavaScript client script)

#### B. Asset Privacy & Exclusions (`.assetsignore`)
Verifies that no server scripts, configs, git internals, internal docs, or staging assets are leaked or served:
- [PASS] `GET /original/` -> HTTP 404
- [PASS] `GET /original/index.original.html` -> HTTP 404
- [PASS] `GET /docs/` -> HTTP 404
- [PASS] `GET /docs/REPORT.md` -> HTTP 404
- [PASS] `GET /tools/` -> HTTP 404
- [PASS] `GET /tools/verify_site.py` -> HTTP 404
- [PASS] `GET /prompt.txt` -> HTTP 404
- [PASS] `GET /worker/index.js` -> HTTP 404
- [PASS] `GET /wrangler.jsonc` -> HTTP 404
- [PASS] `GET /content/pages.json` -> HTTP 404
- [PASS] `GET /.dev.vars` -> HTTP 404
- [PASS] `GET /.dev.vars.example` -> HTTP 404

#### C. Security Headers (`_headers`)
Verifies security headers applied to responses:
- [PASS] `X-Content-Type-Options: nosniff`
- [PASS] `Referrer-Policy: strict-origin-when-cross-origin`
- [PASS] `X-Frame-Options: DENY`
- [PASS] `Content-Security-Policy: default-src 'self'; script-src 'self' https://challenges.cloudflare.com; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; frame-src https://challenges.cloudflare.com; connect-src 'self' https://challenges.cloudflare.com; base-uri 'self'; form-action 'self'; frame-ancestors 'none'`

#### D. HTTP Method & Strict Origin Policy
- [PASS] `GET /api/contact` -> HTTP 405 Method Not Allowed (`Allow: POST`, JSON error response)
- [PASS] Origin Policy: No Origin & No Sec-Fetch-Site -> HTTP 403 Forbidden
- [PASS] Origin Policy: Wrong Cross-Site Origin (`https://malicious-site.example.com`) -> HTTP 403 Forbidden
- [PASS] Origin Policy: OPTIONS Preflight Wrong Origin -> HTTP 403 Forbidden
- [PASS] Origin Policy: OPTIONS Preflight Allowed Origin (`http://localhost:8787`) -> HTTP 204 (`Access-Control-Allow-Origin: http://localhost:8787`)
- [PASS] Origin Policy: No Origin with `Sec-Fetch-Site: same-origin` -> Passes Origin Stage (HTTP 200 `{ok: true, delivered: false}`)
- [PASS] Origin Policy: Request URL Own Origin (`http://127.0.0.1:8787`) -> Passes Origin Stage (HTTP 200 `{ok: true, delivered: false}`)
- [PASS] Origin Policy: `ALLOWED_ORIGINS` Header (`http://localhost:8787`) -> Passes Origin Stage (HTTP 200 `{ok: true, delivered: false}`)

#### E. JSON-Only Content-Type Contract (RFC 8259 Media Type Validation)
- [PASS] Content-Type Contract: `application/json` Accepted -> HTTP 200 `{ok: true, delivered: false}`
- [PASS] Content-Type Contract: `application/json; charset=utf-8` Accepted -> HTTP 200 `{ok: true, delivered: false}`
- [PASS] Content-Type Contract: `text/plain` Rejected -> HTTP 415 (`{"ok":false,"error":"Unsupported media type"}`)
- [PASS] Content-Type Contract: Missing Content-Type Rejected -> HTTP 415 (`{"ok":false,"error":"Unsupported media type"}`)

#### F. Request Size Limits
- [PASS] Request body > 20 KB (21,000 bytes) -> HTTP 413 Payload Too Large

#### G. Server-Side Validation (Mirroring Client Validation)
- [PASS] Missing name -> HTTP 400 (`Invalid name`)
- [PASS] Oversized name (>100 characters) -> HTTP 400 (`Invalid name`)
- [PASS] Oversized company (>150 characters) -> HTTP 400 (`Invalid company`)
- [PASS] Missing phone number -> HTTP 400 (`Invalid phone`)
- [PASS] Oversized phone number (>30 characters) -> HTTP 400 (`Invalid phone`)
- [PASS] Invalid phone characters (`123-abc-4567`) -> HTTP 400 (`Invalid phone`)
- [PASS] Missing email -> HTTP 400 (`Invalid email`)
- [PASS] Invalid email format (`not-an-email`) -> HTTP 400 (`Invalid email`)
- [PASS] Oversized email (>254 characters) -> HTTP 400 (`Invalid email`)
- [PASS] CRLF in email (`user@example.com\r\nBcc: evil@example.com`) -> HTTP 400 (`Invalid email`)
- [PASS] Missing message -> HTTP 400 (`Invalid message`)
- [PASS] Oversized message (>5000 characters) -> HTTP 400 (`Invalid message`)
- [PASS] Unknown fields in JSON payload (`unexpectedField: illegal`) -> HTTP 400 (`Invalid request payload`)

#### H. Cloudflare Turnstile Synthetic Verification (Configuration A)
- [PASS] Missing Turnstile token -> HTTP 400 (`Security token required`)
- [PASS] Documented dummy token (`XXXX.DUMMY.TOKEN.XXXX`) with Pass Secret -> HTTP 200 (Cloudflare siteverify succeeds)

#### I. Honeypot Anti-Spam
- [PASS] Populated `website` field -> HTTP 200 `{ok: true}` returned immediately without email delivery or lead logging

#### J. Valid Submission & Staging Delivery
- [PASS] Valid submission payload with documented dummy token -> HTTP 200 `{ok: true, delivered: false}`
- [PASS] Response header `Cache-Control: no-store` verified

#### K. Header Injection Defense
- [PASS] CRLF in name (`Jane\r\nDoe\r\nSubject: Injected`) sanitized cleanly to single line, preventing email header manipulation

---

### Configuration B: Cloudflare Documented Always-Fail Test Secret (`TURNSTILE_SECRET=2x0000000000000000000000000000000AA`)

#### L. Turnstile Token Rejection
- [PASS] Missing Turnstile token -> HTTP 400 (`Security token required`)
- [PASS] Documented dummy token (`XXXX.DUMMY.TOKEN.XXXX`) verified via Cloudflare siteverify with always-fail secret -> HTTP 400 (`Security verification failed`)

---

## 2. Interactive Browser Testing (375px, 768px, 1280px)

Conducted via browser sessions against live local dev server `http://127.0.0.1:8787/`.

| Viewport | Test Case | Outcome | Console Errors | Status Message Observed |
| :--- | :--- | :--- | :--- | :--- |
| **Desktop (1280x800)** | Empty Submit (Validation) | PASS | 0 | `Please enter your Name.` |
| **Desktop (1280x800)** | Turnstile Rendering | PASS | 0 | Widget rendered above Submit button, theme light |
| **Desktop (1280x800)** | Real Browser Form Submission (Origin Sent) | PASS | 0 | `Thank you! Your consultation request has been received (staging notice: email delivery is not yet configured).` |
| **Tablet (768x1024)** | Responsive Layout | PASS | 0 | Form grid adapted cleanly, no overflow |
| **Tablet (768x1024)** | Valid Form Submission | PASS | 0 | `Thank you! Your consultation request has been received (staging notice: email delivery is not yet configured).` |
| **Mobile (375x667)** | Responsive Layout | PASS | 0 | Form fields stacked vertically, 0 horizontal scroll |
| **Mobile (375x667)** | Valid Form Submission | PASS | 0 | `Thank you! Your consultation request has been received (staging notice: email delivery is not yet configured).` |

---

## 3. Dry-Run Asset Upload Verification (`wrangler deploy --dry-run`)

- **Total assets scanned**: 959 files
- **Total assets retained for deployment**: 60 static public files
- **Total Upload Size**: 8.86 KiB (gzip: 2.54 KiB)
- **Excluded paths**: Confirmed 100% absent from edge upload list; all return HTTP 404 under `wrangler dev`.
