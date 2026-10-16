# TASK: Add a free Cloudflare backend for the contact form (Stage A: works on *.workers.dev, no domain yet)

Repo: itshim998/HireHR. Create a new branch `feature/contact-worker` from the latest `ready-site` and work there. Small commits; push with `git push -u origin feature/contact-worker` and confirm with `git ls-remote --heads origin feature/contact-worker`.

## RULES (unchanged)
- Do not invent information (no new company claims or marketing copy). Do not delete existing content, and do not move existing files.
- **Serious blockers: stop immediately and report in the standard format** (🚫 BLOCKER / What / Where / Why it's serious / Options / I have stopped and am waiting for your decision). Serious here includes: Cloudflare docs show that sending to verified destination addresses from a Worker is NOT available on the Workers Free plan; the Turnstile widget cannot be used on a `workers.dev` hostname; any step that would require a paid plan, a credit card, or a secret/token from me in chat; the push failing.
- **Never commit secrets** (API tokens, the Turnstile secret key, my email address). The repo is public. Do not ask me to paste secrets into chat and do not run `wrangler secret put` yourself with real values; document the commands for me to run.
- Total cost must stay at $0. Do not add paid services, and do not add Resend or any third-party email service.

## CONTEXT
- The static site is at the repo root (index.html, inner pages, css/, js/, assets/). The form is `#consultation-form` on `index.html`, handled in `js/main.js` (section 4). It already validates client-side and, when `FORM_ENDPOINT` is set, POSTs JSON `{name, company, phone, email, message}` (phone = country code + number). Currently `FORM_ENDPOINT = null`.
- Hosting target: **Cloudflare Workers with Static Assets** (one deployment = static site + API Worker, same origin, no CORS). Pages Functions is acceptable only if Workers static assets is impossible; explain why in the report.
- Email, later (Stage B, after I buy the domain): Cloudflare Email Routing receives mail for `employer@` and `jobseeker@`; the Worker emails me via Cloudflare's own Email Service `send_email` binding to a verified destination address only. **Read the current docs at developers.cloudflare.com/email-service and use the currently documented binding API**, since parts of it were beta; if it differs from what is described here, adapt and note it in the report.
- Until the domain exists, real email delivery cannot be tested. Stage A must therefore be complete and testable with `MAIL_MODE=log`.

## DELIVERABLES

### 1. Worker (`worker/index.js`, plain JavaScript, no framework, minimal or zero dependencies)
- `POST /api/contact` only (others → 405). JSON only, request body ≤ 20 KB.
- **Origin check:** accept only origins listed in env var `ALLOWED_ORIGINS` (comma-separated). Default for Stage A: the workers.dev URL(s) plus `http://localhost:8787`. Stage B adds `https://hirehrservices.com` and `https://www.hirehrservices.com`. No wildcard CORS.
- **Server-side validation (mirrors the client):** name required ≤ 100 chars; company optional ≤ 150; phone required, ≤ 30 chars, digits, `+`, spaces, `-`, parentheses only; email required, valid, ≤ 254; message required ≤ 5000. Trim all fields, reject unknown fields, return `400` with `{ok:false, error:"<generic message>"}`.
- **Header injection:** strip CR/LF from anything used in subject or headers (Reply-To, name).
- **Honeypot:** hidden field `website`. If filled, return `200 {ok:true}` without doing anything (bots shouldn't learn they were caught).
- **Turnstile:** require `turnstileToken`, verify it server-side via Cloudflare's siteverify endpoint using secret `TURNSTILE_SECRET`; on failure return `400`.
- **Email step with `MAIL_MODE`:**
  - `log` (default): log a compact line (never log the message body or personal data outside local dev) and return `200 {ok:true, delivered:false}`.
  - `send`: send ONE plain-text email using the Email Service binding named `EMAIL`: `to` = secret `NOTIFY_TO`, `from` = var `MAIL_FROM`, `replyTo` = visitor's email, subject `New consultation request: <name>`, body listing Name, Company, Phone, Email, Message. On any send failure return `502 {ok:false}`. **Never report success if the email was not sent.**
- Responses: always JSON; no stack traces; `Cache-Control: no-store`.
- Config via `wrangler.jsonc`: `name: "hirehr"`, `main: "worker/index.js"`, current `compatibility_date`, `assets` with `directory: "./"`, `binding: "ASSETS"`, `html_handling: "auto-trailing-slash"`, `not_found_handling: "404-page"`, and `run_worker_first: ["/api/*"]` so static pages are served directly without invoking the Worker; `send_email: [{ "name": "EMAIL" }]` (unrestricted binding, since the recipient comes from the `NOTIFY_TO` secret, never hardcoded); `vars`: `ALLOWED_ORIGINS`, `MAIL_MODE: "log"`, `MAIL_FROM: ""`. `observability` enabled if free.
- `.assetsignore` at the assets root must exclude everything that is not public: `worker/`, `wrangler.jsonc`, `node_modules/`, `.git/`, `original/`, `docs/`, `tools/`, `prompt.txt`, `README.md`, `package*.json`, `.dev.vars`. Verify with `wrangler deploy --dry-run` (or equivalent) that the uploaded asset list contains only site files.
- Add `.dev.vars.example` (fake values, committed) and put `.dev.vars` in `.gitignore`.

### 2. Frontend changes (minimal, no copy changes)
- Set `FORM_ENDPOINT = '/api/contact'` in `js/main.js`. Keep the existing client validation and messages. Keep the existing `null` branch as a fallback, but if the Worker returns `{ok:true, delivered:false}` show a neutral staging notice instead of the "sent successfully" message.
- Add a hidden honeypot input `website` (visually hidden, `tabindex="-1"`, `autocomplete="off"`, `aria-hidden="true"`) and the **Turnstile widget** (explicit rendering, theme light) above the submit button, plus the `turnstileToken` in the payload. Put the **public** site key in one clearly marked constant or `data-sitekey`; for now use Cloudflare's documented always-pass test site key, with a comment to replace it. Reset the widget after each submit attempt. Handle widget load failure gracefully (clear error message, no JS exceptions).
- Add a `_headers` file (security headers: `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `X-Frame-Options: DENY` or CSP frame-ancestors, and a CSP that allows only self plus `https://challenges.cloudflare.com` for Turnstile). Verify nothing on the site breaks: slider, images, form, fonts, intl dial-code list.
- Do not change any visible text, other than what is needed for the neutral staging notice.

### 3. Tests and verification (record in `docs/VERIFY_BACKEND.md`)
Run `npx wrangler dev` and test with curl/script: valid submission → 200; each missing/oversize/invalid field → 400; honeypot filled → 200 and nothing logged as a lead; wrong Origin → 403; GET → 405; invalid/missing Turnstile token (use Cloudflare's documented test secret that always fails) → 400; CRLF in name/email → rejected or sanitized; body > 20 KB → 413. Then test the actual form in the browser at 375 / 768 / 1280 px (success path with the always-pass test keys, error states, no console errors). Confirm static pages are served without invoking the Worker, and `/original/`, `/docs/`, `/tools/`, `/prompt.txt`, `/worker/index.js`, `/wrangler.jsonc` return 404.

### 4. Docs
- `docs/DEPLOY.md`: exact, numbered steps for me, the site owner. **Stage A:** create a free Cloudflare account; connect the GitHub repo via Workers Builds (dashboard, Workers & Pages → Create → Import a repository) or deploy with `npx wrangler deploy`; create a Turnstile widget (real site key + secret); set `TURNSTILE_SECRET` as a secret and replace the test site key; set `ALLOWED_ORIGINS` to the real workers.dev URL; smoke test. **Stage B (written now, executed later):** register hirehrservices.com, add it to Cloudflare, enable Email Routing and create `employer@` and `jobseeker@`, verify my destination inbox, add the `NOTIFY_TO` secret and `MAIL_FROM` var (a sender address on the domain), set `MAIL_MODE=send`, add `https://hirehrservices.com` and `https://www.hirehrservices.com` to `ALLOWED_ORIGINS`, attach the custom domain (and a www→apex redirect), add the domain to the Turnstile widget hostnames, run the end-to-end test (form → email arrives with correct Reply-To; sending to employer@ and jobseeker@ forwards), then optionally disable the workers.dev URL. Include the "dropped" label gotcha for Worker-sent mail in the Email Routing dashboard.
- Update `README.md` (architecture, env vars, local dev) and append a "Backend (Stage A)" section to `docs/REPORT.md` (what was built, decisions, anything unverified, deviations).

## FINAL REPORT (in chat)
What was built; the files added or changed; the test results; commit hash; push confirmation; any doc discrepancies you found about the Email Service binding; open questions for me.

## ADDENDUM (apply on top of everything above)

1. **More paths to keep private.** The content branch added a `content/` directory (refined-copy.md, pages.json). In addition to the paths already listed, `.assetsignore` must also exclude `content/`, `.gitignore`, `.dev.vars.example` and `.github/` (if it exists). Verify with the dry-run asset list, and also confirm that `/content/pages.json` returns 404 under `wrangler dev`.

2. **Same-origin Origin check.** In addition to the `ALLOWED_ORIGINS` list, accept a request whose `Origin` header equals the origin of the request URL itself (`new URL(request.url).origin`). That way the form works on any hostname the Worker is served from (workers.dev now, hirehrservices.com later, localhost in dev) without manual configuration, and `ALLOWED_ORIGINS` is only for extra origins. A cross-site Origin must still be rejected with 403. Keep the "wrong Origin → 403" test.

3. **Email binding must not block Stage A.** If declaring the `send_email` binding makes `wrangler dev` or `wrangler deploy` fail before Email Routing exists on a domain, leave the binding commented out in `wrangler.jsonc` with a clear "enable in Stage B" note, and document that in `docs/DEPLOY.md`. In every case the Worker must treat a missing `env.EMAIL` as "not configured": fine in `MAIL_MODE=log`, and in `send` mode it must fail closed (`502 {ok:false}`) and never claim success.