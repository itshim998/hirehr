# HireHR Deployment Guide (`docs/DEPLOY.md`)

This guide provides exact, step-by-step instructions for deploying and maintaining the **HireHR** website and backend on Cloudflare.

The architecture uses **Cloudflare Workers with Static Assets** (a single unified deployment where static HTML/CSS/assets and the `/api/contact` Worker run under the same origin at zero cost).

- **Production Branch:** `main` is the designated production branch. A push to `main` automatically triggers a live production deployment to `https://hirehrservices.com`.
- **Design System Location:** The design system is documented in full in [`docs/DESIGN_SYSTEM.md`](DESIGN_SYSTEM.md), with tokens and rules implemented in [`css/style.css`](../css/style.css) and motion infrastructure in [`js/ui.js`](../js/ui.js).
- **Rollback Procedure:** Refer to [`docs/ROLLBACK.md`](ROLLBACK.md) for instructions on reverting production commits if needed.

---

## Stage A: Free Staging Deployment (*.workers.dev)
*Objective: Deploy the website and contact form backend on Cloudflare's free tier with simulation/log mode before purchasing or connecting the custom domain.*

### 1. Create a Free Cloudflare Account
1. Visit [https://dash.cloudflare.com/sign-up](https://dash.cloudflare.com/sign-up) and create a free account.
2. Verify your email address. No credit card or paid plan is required.

### 2. Deploy via Workers Builds (GitHub Integration) OR Wrangler CLI

#### Option A: Dashboard Deployment via Workers Builds (Recommended)
1. In the Cloudflare Dashboard, navigate to **Compute (Workers) > Workers & Pages**.
2. Click **Create** > **Import a repository** (Workers Builds).
3. Connect your GitHub account and authorize access to `itshim998/HireHR`.
4. Select the repository and production branch (`main`).
5. Configure the build settings:
   - **Framework preset**: None
   - **Build command**: (Leave empty, pure static site)
   - **Deploy command**: `npx wrangler deploy`
6. Click **Save and Deploy**. Cloudflare will assign a staging URL: `https://hirehr.<your-subdomain>.workers.dev`.

#### Option B: Direct CLI Deployment via Wrangler
1. Authenticate with Cloudflare locally:
   ```bash
   npx wrangler login
   ```
2. Verify deployment assets using dry-run:
   ```bash
   npx wrangler deploy --dry-run
   ```
3. Deploy to your free `workers.dev` subdomain:
   ```bash
   npx wrangler deploy
   ```
4. Note your assigned `https://hirehr.<your-subdomain>.workers.dev` URL.

---

### 3. Create a Cloudflare Turnstile Widget
1. In the Cloudflare Dashboard, go to **Turnstile** in the left sidebar.
2. Click **Add widget**.
3. Fill in the widget details:
   - **Widget name**: `HireHR Contact Form`
   - **Domain**: Add your assigned workers.dev domain (e.g., `hirehr.<your-subdomain>.workers.dev`) and `localhost` (for local dev testing).
   - **Widget Mode**: `Managed` (or `Non-interactive`)
4. Click **Create**.
5. Copy your generated **Site Key** and **Secret Key**.

---

### 4. Configure Production Turnstile Keys
1. **Set the Secret Key on Cloudflare** (never commit real secrets to Git):
   - Using the Dashboard: Navigate to **Workers & Pages > hirehr > Settings > Variables and Secrets > Add Secret**. Set variable name `TURNSTILE_SECRET` and paste your secret key.
   - OR using Wrangler CLI:
     ```bash
     npx wrangler secret put TURNSTILE_SECRET
     ```
     *(Paste your real Turnstile secret key when prompted).*
2. **Update the Public Site Key in Code**:
   - The Turnstile site key is maintained in exactly one place: `js/main.js` (`TURNSTILE_SITE_KEY`). Replace the dummy test site key in `const TURNSTILE_SITE_KEY = '...';` with your real production site key. (Do not add a `data-sitekey` attribute to `index.html`).
   > [!NOTE]
   > Tokens from the dummy test site key (`1x00000000000000000000AA`) only verify against Cloudflare's dummy test secrets, so the staging and production deployments must use a real Turnstile site key + secret pair to verify live visitors.
3. Commit and push the updated public site key to your repository.

---

### 5. Configure Allowed Origins
1. In Cloudflare Dashboard, go to **Workers & Pages > hirehr > Settings > Variables and Secrets**.
2. Edit environment variable `ALLOWED_ORIGINS`:
   ```
   https://hirehr.<your-subdomain>.workers.dev, http://localhost:8787
   ```
   *(Note: The Worker automatically allows same-origin requests, but explicit entry ensures external dev/staging tools connect seamlessly).*

---

### 6. Smoke Test (Stage A)
1. Open `https://hirehr.<your-subdomain>.workers.dev/` in your browser.
2. Verify all pages, images, and the hero slider function smoothly.
3. Scroll to the **Request a Free Consultation** form.
4. Verify the Turnstile widget renders and completes.
5. Submit the form with valid details:
   - Notice displayed: `Thank you! Your consultation request has been received (staging notice: email delivery is not yet configured).`
   - Check real-time logs via `npx wrangler tail hirehr` or the Cloudflare dashboard **Logs** tab:
     You should see: `[contact-worker] Consultation inquiry received in log mode at <ISO-timestamp>`.
6. Test error validation (empty submit, wrong email format) to ensure clean client feedback.

---

## Stage B: Production Domain & Live Email Routing (hirehrservices.com)
*Objective: Connect custom domain `hirehrservices.com`, configure Cloudflare Email Routing for business inboxes, and activate live email notifications.*

> [!WARNING]
> **Do NOT onboard a Cloudflare Email Sending domain.** It is not needed to send to your own verified destination address, and general Email Sending requires the paid Workers plan. Only Email Routing + a verified destination address + the `send_email` binding are used.

### 1. Register & Add Domain to Cloudflare
1. Register `hirehrservices.com` (via Cloudflare Registrar or your preferred registrar).
2. In Cloudflare Dashboard, click **Add a site** and enter `hirehrservices.com`.
3. Select the **Free** plan.
4. If registered externally, update your domain's nameservers at your registrar to point to the Cloudflare nameservers provided.

---

### 2. Configure Cloudflare Email Routing
1. In the Cloudflare Dashboard, select `hirehrservices.com` and click **Email > Email Routing**.
2. Click **Get Started** to enable Email Routing. Cloudflare will automatically add the required MX and SPF/TXT DNS records.
3. Under **Destination addresses**, click **Add destination address**:
   - Enter your personal or company inbox where you want to receive inquiries (e.g. `yourname@gmail.com`).
   - Check your destination inbox for the verification email from Cloudflare and click the verification link.
4. Under **Routing rules**, create custom addresses:
   - `info@hirehrservices.com` -> Forward to your verified destination address.
   *(Note: Legacy routing rules for `employer@hirehrservices.com` and `jobseeker@hirehrservices.com` may be retained as secondary forwarders during transition, but the single public identity is `info@hirehrservices.com`).*
5. Test forwarding: Send an email from a personal account to `info@hirehrservices.com` and confirm it arrives in your inbox.

---

### 3. Enable Email Sending Binding in Wrangler
1. Open `wrangler.jsonc` in your codebase.
2. Uncomment the `send_email` binding block:
   ```jsonc
   "send_email": [
     {
       "name": "EMAIL"
     }
   ],
   ```
3. Update environment variables in `wrangler.jsonc` (or via Cloudflare Dashboard):
   - `MAIL_MODE`: Change from `"log"` to `"send"`
   - `MAIL_FROM`: Set to `"info@hirehrservices.com"`
4. Add the notification recipient secret:
   ```bash
   npx wrangler secret put NOTIFY_TO
   ```
   *(Enter your verified destination address, e.g. `yourname@gmail.com`).*

---

### 4. Single Test Send to Verified Destination Address
> [!IMPORTANT]
> The first step immediately after enabling the binding is a single test send to the verified destination address.
> If it fails with a plan, permission, or availability error, **STOP immediately and report it as a blocker; do NOT upgrade anything.**

1. Trigger a single test submission (via form or POST request to `/api/contact`).
2. Verify delivery in your verified destination inbox (`NOTIFY_TO`).
3. If any plan, permission, or availability error occurs: STOP and report as a blocker.

---

### 5. Update Allowed Origins & Turnstile Hostnames
1. In `wrangler.jsonc` (and Cloudflare Dashboard under **Variables and Secrets**), update `ALLOWED_ORIGINS`:
   ```
   https://hirehrservices.com, https://www.hirehrservices.com, http://localhost:8787
   ```
2. In Cloudflare Dashboard, navigate to **Turnstile**:
   - Edit the `HireHR Contact Form` widget.
   - Under **Hostname Management**, add `hirehrservices.com` and `www.hirehrservices.com`.
   - Save changes.

---

### 6. Attach Custom Domain & Configure Apex / WWW
1. In Cloudflare Dashboard, navigate to **Workers & Pages > hirehr > Settings > Domains & Routes**.
2. Click **Add > Custom Domain**:
   - Enter `hirehrservices.com` and confirm. Cloudflare will automatically configure the DNS record.
3. To handle `www.hirehrservices.com`, configure a redirect rule:
   - In your zone dashboard for `hirehrservices.com`, go to **Rules > Redirect Rules**.
   - Create a rule: When incoming request hostname equals `www.hirehrservices.com`, perform a **Dynamic Redirect** (301) to `concat("https://hirehrservices.com", http.request.uri.path)`.
   - (Alternatively, add `www.hirehrservices.com` as a second Custom Domain pointing to the same Worker).

---

### 7. End-to-End Live Testing
1. Visit `https://hirehrservices.com/` in your browser.
2. Submit a consultation request through `#consultation-form`.
3. Verify the user feedback displays:
   `Thank you! Your consultation request has been sent successfully.`
4. Check your destination inbox:
   - Confirm email arrives from `info@hirehrservices.com`.
   - Subject: `New consultation request: <Submitted Name>`.
   - Reply-To: Set to the visitor's email address (clicking **Reply** should directly reply to the visitor).
   - Body contains Name, Company, Phone, Email, and Message.

---

### 8. Important Cloudflare Email Routing Dashboard Note ("Dropped" Label Gotcha)
> [!NOTE]
> In the Cloudflare Dashboard under **Email > Email Routing > Activity Log**, you may notice outbound messages dispatched by the Worker's `send_email` binding marked with a status of **"dropped"** or **"unhandled"**.
> 
> **Do not panic**: This is a known Cloudflare dashboard labeling quirk. Cloudflare's Email Routing activity log is primarily designed to track *inbound* forwarded emails. When an outbound email originates directly inside a Worker via `env.EMAIL.send()`, the inbound routing engine flags it as "dropped from inbound routing" because it did not trigger an inbound forwarding rule, even though the email was transmitted and delivered to your destination inbox normally. Always verify actual receipt in your inbox.

---

### 9. Optional: Disable workers.dev Subdomain (Post-Stage B)
Once `hirehrservices.com` is live and verified:
1. Navigate to **Workers & Pages > hirehr > Settings > Domains & Routes**.
2. Click the `...` menu next to `hirehr.<your-subdomain>.workers.dev` and select **Disable**.
3. All traffic will now exclusively route through `https://hirehrservices.com`.

---

### 10. Outbound Reply Workflow (Thunderbird + SMTP2GO)
To send email replies to inquiries directly as `info@hirehrservices.com` from a desktop email client with verified SPF/DKIM authentication:

1. **SMTP2GO Sender Domain Verification**:
   - In the SMTP2GO dashboard, add and verify sender domain `hirehrservices.com`.
   - Add the DKIM CNAME records and SPF TXT record specified by SMTP2GO into Cloudflare DNS for `hirehrservices.com`.
2. **Dedicated SMTP User**:
   - In SMTP2GO under **Settings > SMTP Users**, create a dedicated SMTP user for `info@hirehrservices.com`.
3. **Thunderbird Configuration**:
   - **Identity Settings**:
     - Your Name: `HireHR Services`
     - Email Address: `info@hirehrservices.com`
     - Reply-to Address: `info@hirehrservices.com`
   - **Outgoing Server (SMTP)**:
     - Server Name: `mail.smtp2go.com`
     - Port: `587` (STARTTLS) or `465` (SSL/TLS)
     - Authentication method: Normal password
     - User Name: `<your-smtp2go-username>`
4. **Replying Workflow**:
   - **Form submissions dispatched by Worker**: The Worker dispatches inquiries to your destination inbox with `Reply-To` set to the visitor's email address. Clicking **Reply** in Thunderbird addresses the reply directly to the visitor while sending From `info@hirehrservices.com` authenticated via SMTP2GO.
   - **Direct inbound emails forwarded by Cloudflare**: Inquiries sent directly to `info@hirehrservices.com` are forwarded by Cloudflare Email Routing to your inbox; replying from Thunderbird sends From `info@hirehrservices.com` through SMTP2GO with full DKIM and SPF alignment.

