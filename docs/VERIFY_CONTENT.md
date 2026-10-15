# Content and Site Verification Suite (docs/VERIFY_CONTENT.md)

This document aggregates the comprehensive verification outputs from both 	ools/verify_content.py (Refined Content, Forbidden Terms, Placeholder Integrity) and 	ools/verify_site.py (No-loss original text verification, link resolution, dead domain references, and original snapshot integrity).

---

# Content Verification Report (`docs/VERIFY_CONTENT.md`)
Executed according to Phase: VERIFICATION (must pass) in `prompt.txt`.

## 1. Refined Copy Verbatim Assertions (33 items checked)

- [PASS] `about.p1` on `about-us/index.html`: appears exactly once, verbatim.
- [PASS] `about.p2` on `about-us/index.html`: appears exactly once, verbatim.
- [PASS] `about.p3` on `about-us/index.html`: appears exactly once, verbatim.
- [PASS] `bgv.h2` on `background-verification-service/index.html`: appears exactly once, verbatim.
- [PASS] `bgv.p1` on `background-verification-service/index.html`: appears exactly once, verbatim.
- [PASS] `career_advice.p1` on `career-advice/index.html`: appears exactly once, verbatim.
- [PASS] `contract.p1` on `contract-hiring-solutions/index.html`: appears exactly once, verbatim.
- [PASS] `contract.p2` on `contract-hiring-solutions/index.html`: appears exactly once, verbatim.
- [PASS] `contract_to_hire.p1` on `contract-to-hire-solutions/index.html`: appears exactly once, verbatim.
- [PASS] `home.card.it` on `index.html`: appears exactly once, verbatim.
- [PASS] `home.card.ites` on `index.html`: appears exactly once, verbatim.
- [PASS] `home.card.nonit` on `index.html`: appears exactly once, verbatim.
- [PASS] `home.who` on `index.html`: appears exactly once, verbatim.
- [PASS] `home.why.coordination` on `index.html`: appears exactly once, verbatim.
- [PASS] `home.why.cost` on `index.html`: appears exactly once, verbatim.
- [PASS] `home.why.database` on `index.html`: appears exactly once, verbatim.
- [PASS] `home.why.experience` on `index.html`: appears exactly once, verbatim.
- [PASS] `home.why.time` on `index.html`: appears exactly once, verbatim.
- [PASS] `home.why.tools` on `index.html`: appears exactly once, verbatim.
- [PASS] `job_seekers.interview.h2` on `job-seekers/index.html`: appears exactly once, verbatim.
- [PASS] `job_seekers.interview.p` on `job-seekers/index.html`: appears exactly once, verbatim.
- [PASS] `job_seekers.resume.h2` on `job-seekers/index.html`: appears exactly once, verbatim.
- [PASS] `job_seekers.resume.p` on `job-seekers/index.html`: appears exactly once, verbatim.
- [PASS] `permanent.p1` on `permanent-hiring-solutions/index.html`: appears exactly once, verbatim.
- [PASS] `permanent.p2` on `permanent-hiring-solutions/index.html`: appears exactly once, verbatim.
- [PASS] `rpo.p1` on `recruitment-process-outsourcing/index.html`: appears exactly once, verbatim.
- [PASS] `rpo.p2` on `recruitment-process-outsourcing/index.html`: appears exactly once, verbatim.
- [PASS] `specialty.it.h2` on `our-specialty/index.html`: appears exactly once, verbatim.
- [PASS] `specialty.it.p` on `our-specialty/index.html`: appears exactly once, verbatim.
- [PASS] `specialty.ites.h2` on `our-specialty/index.html`: appears exactly once, verbatim.
- [PASS] `specialty.ites.p` on `our-specialty/index.html`: appears exactly once, verbatim.
- [PASS] `specialty.nonit.h2` on `our-specialty/index.html`: appears exactly once, verbatim.
- [PASS] `specialty.nonit.p` on `our-specialty/index.html`: appears exactly once, verbatim.

## 2. Forbidden Words and Character Assertions

- [PASS] **No `consultancy` (case-insensitive)** found in site copy on any site page.
- [PASS] **No em dash (`—` / `&mdash;`)** found on any site page.
- [PASS] **No `emloyer` typo** found on any site page.
- [PASS] **`data-placeholder` remains ONLY on `contact-us`**.

### RESULT: ALL CONTENT VERIFICATION CHECKS PASSED (100%)


---

# Site Verification Report (`docs/VERIFY.md`)
Generated as required by Phase 4 of `prompt.txt`.

## 1. No-Loss Text Content Verification
- **Original visible unique strings count**: 62
- **New site cumulative unique strings count**: 102
- **User-authorized intentional removals**: 17 (Copyright © 2021 | Design & Developed By Zauca, Facebook, HireHR Consultancy Services is a Recruitment service provider with focus on IT and ITes Talent. We are located in Kolkata, India. If you are an emloyer looking to enhance your talent requirement function through facilitating a great candidate experience and reduced time to hire, we can be your partners!, HireHR consultancy services, Twitter, We assist non IT Hiring from support staff level to management level (CEO/Director)., We can help you to find most suitable IT profiles for your internal and client’s IT hiring. Starting from Java, .Net to modern days Cloud, AI, ML we have ready resources for most of the IT skills to fulfill all your IT requirements., We can help you to find right fit for your BPO, KPO division. We have expertise in Bulk hiring and Campus hiring in ITES recruitment field., We do have vast Database of IT and non IT talent to ensure the availability of the resource you need., We emphasis on proper and timely coordination with our customers to ensure customer’s satisfaction and further growth of business relationship., We ensure you get the best possible service at competitive cost., We have a pool of experienced Talent Acquisition specialists to serve your requirements. They are expert in end to end recruitment including sourcing, shortlisting and interviewing candidates., We refer best available Job portal when look for resources. We also emphasis on social networking, head hunting when look for right Talent to meet your requirements., We understand the importance of time. Our qualified recruiters are capable of delivering the talents within quick turnaround time., Welcome to HireHR Consultancy Services, employer@hirehrconsultancy.com, jobseeker@hirehrconsultancy.com)
- **Unauthorized missing strings from new site**: 0

 [PASS] **100% of required original visible text strings are preserved across the new site (with explicit user-authorized removals).**

## 2. Internal Link Resolution Verification
 [PASS] **All internal relative hyperlinks resolve to valid local files.**

## 3. Runtime Dead Domain Reference Check
 [PASS] **Zero runtime stylesheet, script, or image requests to dead domain `hirehrconsultancy.com`. All active assets are local.**

## 4. Git Backup & Original Integrity Verification
- Original backup file: `original/index.original.html`
- SHA256: `01d50fc22237d9b17a81e99b76260106de824382893fb17bda3d4b7d0a586a5a` (Verified pristine)
- Active working branch: `ready-site`


