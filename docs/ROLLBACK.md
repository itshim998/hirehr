# HireHR Production Rollback Procedure (`docs/ROLLBACK.md`)

This document outlines the standard and emergency rollback procedures for the `main` branch of `itshim998/HireHR`.

> [!CAUTION]
> **DO NOT EXECUTE THIS PROCEDURE UNLESS AN EMERGENCY ROLLBACK IS REQUIRED AND AUTHORIZED BY THE SITE OWNER.**
> A push to `main` immediately triggers a Cloudflare Workers production deploy.

---

## 1. Revert-Based Procedure (Recommended)

To cleanly undo the design upgrade on `main` without rewriting Git history:

```bash
# 1. Ensure working directory is clean and up to date on main
git checkout main
git pull --ff-only origin main

# 2. Revert all commits introduced by the design upgrade (42f4686 to current HEAD) into the index
git revert --no-commit 42f4686..HEAD

# 3. Create a single, atomic revert commit
git commit -m "revert: rollback design upgrade to production baseline (42f4686)"

# 4. Verify text and content integrity against the pre-upgrade backup branch
python tools/verify_text_unchanged.py --base backup/main-before-design-upgrade
python tools/verify_content.py
python tools/verify_site.py

# 5. Push to main to trigger automatic Cloudflare production redeployment
git push origin main
```

---

## 2. Backup Reference Branch

Before merging the design upgrade into `main`, a dedicated remote backup branch was created and pushed:
- **Backup Branch:** `backup/main-before-design-upgrade`
- **Pinned Commit Hash:** `42f4686866a000eff6b5a0c185be5658475d4502` (`42f4686`)
- **Remote Location:** `https://github.com/itshim998/hirehr/tree/backup/main-before-design-upgrade`

An older pre-production backup branch is also preserved:
- **Branch:** `backup/main-before-production-20261016` (`acf835e`)

---

## 3. Post-Rollback Verification

After pushing the revert commit to `main`, wait ~60s and verify live at `https://hirehrservices.com/`:
1. Check `https://hirehrservices.com/css/style.css` to confirm it no longer references the upgrade tokens.
2. Verify all primary pages return HTTP 200:
   - `/`
   - `/about-us/`
   - `/our-specialty/`
   - `/contact-us/`
3. Verify `POST https://hirehrservices.com/api/contact` returns JSON 4xx (Worker backend intact).
