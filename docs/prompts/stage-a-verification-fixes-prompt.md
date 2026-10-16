# TASK: Final Stage A Verification Fixes for HireHR — Do Not Merge Yet

## Repository and branch

Repository: `itshim998/HireHR`

Continue working on the existing branch: `feature/contact-worker`.

Start by fetching from `origin`, checking out `feature/contact-worker`, and updating it using fast-forward-only pulls. Review the current remote diff against `ready-site` before making changes. Do not create a replacement branch.

The current implementation has already been reviewed. Four previous findings have been addressed, but the verification harness and JSON-only request contract have remaining issues.

## Non-negotiable rules

1. Do not invent business information or change existing website copy, except for the already-authorized neutral staging notice.
2. Do not delete content, move existing files, rewrite Git history, or force-push.
3. Never touch `main`, delete branches, or merge any branch.
4. Preserve `prompt.txt` exactly as it exists on `origin/ready-site`. The Stage A prompt is archived separately; preserve its original contents and clearly label it as historical/superseded without rewriting its text.
5. Never commit real secrets, credentials, API tokens, or the owner's actual destination email address. Never ask the owner to provide a secret in chat.
6. Preserve the established architecture and $0 cost constraint. Do not introduce paid services, third-party email providers, or a separate Cloudflare Email Sending domain-onboarding step.
7. Retain the Stage B test-send gate and its stop rule. Any plan, permission, or availability failure must stop the process for the owner's decision. Never automatically upgrade a plan or work around such a failure.
8. Make small, focused commits. Do not make unrelated refactors.

### Serious-blocker report format

If a serious blocker occurs, stop immediately and report:

BLOCKER  
What: <one sentence>  
Where: <file / line / element>  
Why it's serious: <which rule it touches>  
Options: <2–3 concrete options, with your recommendation>  
I have stopped and am waiting for your decision.

Serious blockers include destructive or irreversible actions, risk of losing user data, a required paid service, a request for real credentials in chat, unavailable repository/tooling/network access, or a failed Git push.

## Deliverable 1 — Correct the Turnstile test fixtures

Review `tools/test_backend.py` against Cloudflare's current official testing documentation:

https://developers.cloudflare.com/turnstile/troubleshooting/testing/

Use Cloudflare's documented dummy-token flow with the corresponding documented test-secret configurations.

- Use the documented dummy token `XXXX.DUMMY.TOKEN.XXXX` for the synthetic successful verification case.
- Use the same documented dummy token with the always-fail test secret to verify rejection.
- Keep the actual Worker dependent exclusively on `env.TURNSTILE_SECRET`.
- Do not restore any logic that chooses a secret based on token content.
- Do not mock or bypass Siteverify in the production Worker.
- Ensure the missing-token, successful-verification, rejected-verification, honeypot, valid-submission, and header-injection tests use consistent fixtures.
- Do not describe synthetic test fixtures as real production verification.

## Deliverable 2 — Make the test harness safe for existing local configuration

Repair the configuration orchestration in `tools/test_backend.py`.

The current `write_dev_vars()` routine overwrites `.dev.vars`, and the `finally` block does not restore the original file. Correct this.

Requirements:

1. Preserve whether `.dev.vars` existed before testing.
2. Preserve its exact original contents and file permissions, if applicable.
3. Restore the exact original file state in a `finally` block, including after exceptions or failed tests.
4. If the file did not previously exist, clean up only the test-created file after testing.
5. Never leave test credentials behind or destroy the owner's existing configuration.
6. If an existing `.dev.vars` file cannot safely be preserved, stop before modifying it and report the blocker.

Correct the test-server lifecycle as well:

- Never assume that an arbitrary process already listening on the test port is using the requested test configuration.
- Either use isolated, known-free ports for both configurations or fail clearly before modifying local files when a required port is occupied.
- Ensure the pass-secret server is the process actually used for the pass-secret suite.
- Stop that process and confirm it has exited before starting the fail-secret suite.
- Verify that the fail-secret suite uses a fresh server with the fail-secret configuration.
- Do not count an existing server response as proof that a newly spawned server started successfully.
- Keep the orchestration deterministic and ensure every spawned process is cleaned up.

## Deliverable 3 — Enforce the JSON-only Worker contract

Update `worker/index.js` to explicitly validate the request content type before treating the request body as JSON.

Requirements:

- Accept `application/json`, including valid parameters such as `charset=utf-8`.
- Reject missing or unsupported content types using an appropriate client-error status, preferably HTTP 415.
- Return the established JSON error format without stack traces.
- Preserve `Cache-Control: no-store` and appropriate response security headers.
- Do not affect the existing size limit, server-side validation, honeypot, strict Origin policy, Turnstile verification, or fail-closed email logic.

Add automated tests for at least:

- JSON with `Content-Type: application/json` is accepted for normal validation.
- JSON with `Content-Type: application/json; charset=utf-8` is accepted.
- A JSON-formatted body with `Content-Type: text/plain` is rejected.
- A JSON-formatted body with no content type is rejected.

Confirm the test helper can send a request without automatically adding the JSON content type.

## Deliverable 4 — Re-run and reconcile the verification report

After making the changes, actually run the verification suite against the updated source.

Run:

- `python3 tools/verify_content.py`
- `python3 tools/verify_site.py`
- `python3 tools/test_backend.py`
- `git diff --check`

Also verify:

- The pass-secret and fail-secret suites run against their intended configurations.
- The real Cloudflare dummy-token behavior agrees with the official documentation.
- The test harness restores `.dev.vars` exactly.
- Tests fail when the wrong verification secret is configured.
- The Worker rejects unsupported content types.
- The form, slider, site assets, and responsive layout remain unaffected.
- The original backup `original/index.original.html` remains unchanged.
- The LinkedIn URL remains `https://www.linkedin.com/in/hirehr-consultancy-services-3149a4206/`.
- No unapproved content changes, secrets, or owner-specific addresses have been introduced.
- `prompt.txt` is still identical to `origin/ready-site`.
- `docs/VERIFY_BACKEND.md` and the Stage A section of `docs/REPORT.md` accurately reflect the latest real test results. Do not retain a 48/48 claim unless the corrected suite actually produces that result.
- The archived Stage A prompt is clearly marked as historical/superseded without rewriting its original body.
- `docs/DEPLOY.md` still prohibits selecting `main` for Stage A.
- The Stage B verified-destination test-send gate and stop rule remain intact, with no separate Email Sending domain-onboarding requirement added.

If a test cannot be executed because of unavailable tooling or network access, report it as not run. Do not invent test output or claim success.

## Git and push requirements

1. Review the entire final diff against `origin/ready-site`.
2. Confirm that only the expected files changed.
3. Commit the focused fixes to the existing `feature/contact-worker` branch.
4. Push with a normal, non-force push.
5. Confirm the remote branch using:

`git ls-remote --heads origin feature/contact-worker`

The returned remote commit must match the commit that was pushed.

Never merge the branch and never modify `main`.

## Final report format

Report:

1. Summary of fixes.
2. Every file changed and why.
3. Actual verification commands and results, including pass/fail counts.
4. Whether `.dev.vars` was preserved and restored correctly.
5. Test-server lifecycle verification.
6. Any tests not run and why.
7. Commit hash and successful remote-push confirmation.
8. Remaining blockers, limitations, and owner decisions required.

Do not declare the branch approved for merge. The owner will review the resulting commit and decide the next step.
