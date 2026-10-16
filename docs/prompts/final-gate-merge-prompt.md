# FINAL GATE: Fix Test Cleanup Failure Handling and Fast-Forward Merge HireHR Stage A

Repository: `itshim998/HireHR`

Branches:
- Feature: `feature/contact-worker`
- Integration: `ready-site`
- Never modify `main`.

## Task

Complete the final safety correction, verify the existing Stage A implementation, and fast-forward merge `feature/contact-worker` into `ready-site` only if every required gate passes.

### 1. Final safety correction

In `tools/test_backend.py`, inspect the `.dev.vars` cleanup logic.

Currently, if restoration fails inside `finally`, the script prints an error but may still exit with a successful test status.

Correct this so that:
- Any failure to restore the original `.dev.vars` bytes and permissions, or remove a test-created file, causes a nonzero process exit.
- The failure is prominently reported without printing secret values.
- The script never reports an overall successful verification when cleanup failed.
- Existing port-conflict handling, configuration isolation, process cleanup, and normal successful restoration remain intact.

Do not perform unrelated refactoring.

### 2. Verify the feature branch

Fetch the latest remote references and work on `feature/contact-worker`. Preserve all user changes.

Run:

```bash
python tools/test_backend.py
python tools/verify_content.py
python tools/verify_site.py
git diff --check
```

Use the repository's actual Python executable if the environment requires `python3`.

Require successful exit codes. Confirm that the test harness safely preserves and restores `.dev.vars`, and that the documented Turnstile dummy-token tests use Cloudflare's official fixtures.

Inspect the complete diff against `origin/ready-site`. Confirm:
- `prompt.txt` is unchanged from `origin/ready-site`.
- `original/index.original.html` is unchanged.
- LinkedIn's original URL is intact.
- No unrelated content or website copy has changed.
- No real secrets or owner-specific destination addresses have been committed.
- The test report accurately records the actual verification results.
- Stage B retains the test-send gate and stop rule.
- Stage B does not introduce a separate Email Sending domain-onboarding requirement.

If port 8787 is occupied, tests fail, cleanup fails, the diff includes unrelated changes, or the remote branch cannot be updated safely, do not merge.

### 3. Commit and push the correction

Make a small commit on `feature/contact-worker`.

Push normally; never force-push. Verify the remote reference:

```bash
git push origin feature/contact-worker
git ls-remote --heads origin feature/contact-worker
```

Confirm the returned SHA matches the pushed feature-branch HEAD.

### 4. Fast-forward merge only if all gates pass

After the feature branch is verified and pushed:

```bash
git checkout ready-site
git pull --ff-only origin ready-site
git merge --ff-only origin/feature/contact-worker
```

If the fast-forward merge fails, stop immediately. Do not reset, rewrite history, or force a merge.

On the resulting `ready-site`, run:

```bash
python tools/verify_content.py
python tools/verify_site.py
git diff --check
```

Push the integration branch:

```bash
git push origin ready-site
git ls-remote --heads origin ready-site
```

Verify the remote SHA matches the merged `ready-site` HEAD. Keep `feature/contact-worker`; do not delete it. Never touch `main`.

### Serious-blocker report format

BLOCKER
What: <one sentence>
Where: <file / line / element>
Why it's serious: <which rule it touches>
Options: <2–3 concrete options, with your recommendation>
I have stopped and am waiting for your decision.

### Final report

Return:
1. Final cleanup fix and commit SHA.
2. Actual results for all verification commands.
3. Confirmation of `.dev.vars` restoration and process cleanup.
4. Feature-branch push confirmation.
5. Whether the fast-forward merge succeeded.
6. Final `ready-site` commit SHA and remote-push confirmation.
7. Any failed tests, blockers, or remaining owner actions.

Do not claim deployment or live email delivery has been verified. Those remain separate, owner-controlled steps.
