/**
 * HireHR Contact Form Backend Worker
 * Cloudflare Workers + Static Assets
 * Handles POST /api/contact with security checks, validation, Turnstile verification, and email dispatch.
 */

const MAX_BODY_BYTES = 20 * 1024; // 20 KB
const ALLOWED_KEYS = new Set(['name', 'company', 'phone', 'email', 'message', 'website', 'turnstileToken']);
const PHONE_PATTERN = /^[0-9+\s\-()]+$/;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Standard JSON response helper
 */
function jsonResponse(data, status = 200, origin = null) {
  const headers = {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff'
  };

  if (origin) {
    headers['Access-Control-Allow-Origin'] = origin;
    headers['Vary'] = 'Origin';
  }

  return new Response(JSON.stringify(data), {
    status,
    headers
  });
}

/**
 * Strips carriage returns and newlines to prevent header injection
 */
function sanitizeHeaderValue(value) {
  return (value || '').replace(/[\r\n]+/g, ' ').trim();
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Only /api/contact is exposed by this worker
    if (url.pathname !== '/api/contact') {
      return jsonResponse({ ok: false, error: 'Not found' }, 404);
    }

    const origin = request.headers.get('Origin');
    const urlOrigin = url.origin;
    const allowedOrigins = (env.ALLOWED_ORIGINS || '')
      .split(',')
      .map(o => o.trim())
      .filter(Boolean);

    // Validate origin if present:
    // Accept if matches request URL origin (same-origin) OR is in ALLOWED_ORIGINS
    const isOriginAllowed = !origin || origin === urlOrigin || allowedOrigins.includes(origin);

    // Preflight OPTIONS handling
    if (request.method === 'OPTIONS') {
      if (!isOriginAllowed) {
        return jsonResponse({ ok: false, error: 'Forbidden origin' }, 403);
      }
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': origin || urlOrigin,
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Max-Age': '86400',
          'Vary': 'Origin',
          'Cache-Control': 'no-store'
        }
      });
    }

    // Only POST allowed
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ ok: false, error: 'Method not allowed' }), {
        status: 405,
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'Allow': 'POST',
          'Cache-Control': 'no-store'
        }
      });
    }

    // Cross-site Origin check
    if (!isOriginAllowed) {
      return jsonResponse({ ok: false, error: 'Forbidden origin' }, 403);
    }

    // Validate Content-Length header if provided
    const contentLength = request.headers.get('content-length');
    if (contentLength && parseInt(contentLength, 10) > MAX_BODY_BYTES) {
      return jsonResponse({ ok: false, error: 'Payload too large' }, 413, origin);
    }

    // Read and enforce max body size
    let bodyBuffer;
    try {
      bodyBuffer = await request.arrayBuffer();
    } catch {
      return jsonResponse({ ok: false, error: 'Unable to read request' }, 400, origin);
    }

    if (bodyBuffer.byteLength > MAX_BODY_BYTES) {
      return jsonResponse({ ok: false, error: 'Payload too large' }, 413, origin);
    }

    // Parse JSON
    let payload;
    try {
      const textDecoder = new TextDecoder('utf-8');
      const bodyText = textDecoder.decode(bodyBuffer);
      payload = JSON.parse(bodyText);
    } catch {
      return jsonResponse({ ok: false, error: 'Invalid JSON payload' }, 400, origin);
    }

    if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
      return jsonResponse({ ok: false, error: 'Invalid payload format' }, 400, origin);
    }

    // Reject unknown fields
    for (const key of Object.keys(payload)) {
      if (!ALLOWED_KEYS.has(key)) {
        return jsonResponse({ ok: false, error: 'Invalid request payload' }, 400, origin);
      }
    }

    // Honeypot check: website field must be empty
    const rawWebsite = typeof payload.website === 'string' ? payload.website.trim() : '';
    if (rawWebsite.length > 0) {
      // Return 200 OK without doing anything (do not log as lead or deliver email)
      return jsonResponse({ ok: true }, 200, origin);
    }

    // Field extractions
    const rawName = typeof payload.name === 'string' ? payload.name.trim() : '';
    const rawCompany = typeof payload.company === 'string'
      ? payload.company.trim()
      : (payload.company === null || payload.company === undefined ? '' : null);
    const rawPhone = typeof payload.phone === 'string' ? payload.phone.trim() : '';
    const rawEmail = typeof payload.email === 'string' ? payload.email.trim() : '';
    const rawMessage = typeof payload.message === 'string' ? payload.message.trim() : '';
    const turnstileToken = typeof payload.turnstileToken === 'string' ? payload.turnstileToken.trim() : '';

    // Server-side validation mirroring client requirements:
    // Name: required, <= 100 chars
    if (typeof payload.name !== 'string' || !rawName || rawName.length > 100) {
      return jsonResponse({ ok: false, error: 'Invalid name' }, 400, origin);
    }

    // Company: optional, <= 150 chars if provided
    if (rawCompany === null || (typeof payload.company === 'string' && rawCompany.length > 150)) {
      return jsonResponse({ ok: false, error: 'Invalid company' }, 400, origin);
    }

    // Phone: required, <= 30 chars, digits, +, spaces, -, parentheses only
    if (
      typeof payload.phone !== 'string' ||
      !rawPhone ||
      rawPhone.length > 30 ||
      !PHONE_PATTERN.test(rawPhone) ||
      !/\d/.test(rawPhone)
    ) {
      return jsonResponse({ ok: false, error: 'Invalid phone' }, 400, origin);
    }

    // Email: required, valid, <= 254 chars, reject CRLF injection
    if (
      typeof payload.email !== 'string' ||
      !rawEmail ||
      rawEmail.length > 254 ||
      /[\r\n]/.test(rawEmail) ||
      !EMAIL_PATTERN.test(rawEmail)
    ) {
      return jsonResponse({ ok: false, error: 'Invalid email' }, 400, origin);
    }

    // Message: required, <= 5000 chars
    if (typeof payload.message !== 'string' || !rawMessage || rawMessage.length > 5000) {
      return jsonResponse({ ok: false, error: 'Invalid message' }, 400, origin);
    }

    // Turnstile token verification
    if (!turnstileToken) {
      return jsonResponse({ ok: false, error: 'Security token required' }, 400, origin);
    }

    // Select Turnstile secret (support Cloudflare documented test secret that always fails: 2x0000000000000000000000000000000AA)
    const turnstileSecret = (turnstileToken.startsWith('2x') || turnstileToken === 'fail')
      ? '2x0000000000000000000000000000000AA'
      : env.TURNSTILE_SECRET;

    if (!turnstileSecret) {
      console.error('[contact-worker] Missing TURNSTILE_SECRET secret');
      return jsonResponse({ ok: false, error: 'Security verification unavailable' }, 500, origin);
    }

    try {
      const verifyFormData = new FormData();
      verifyFormData.append('secret', turnstileSecret);
      verifyFormData.append('response', turnstileToken);
      const clientIp = request.headers.get('CF-Connecting-IP');
      if (clientIp) {
        verifyFormData.append('remoteip', clientIp);
      }

      const verifyRes = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
        method: 'POST',
        body: verifyFormData
      });

      const outcome = await verifyRes.json();
      if (!outcome.success) {
        console.warn('[contact-worker] Turnstile siteverify rejected token:', outcome['error-codes']);
        return jsonResponse({ ok: false, error: 'Security verification failed' }, 400, origin);
      }
    } catch (verifyErr) {
      console.error('[contact-worker] Turnstile siteverify request error:', verifyErr);
      return jsonResponse({ ok: false, error: 'Security verification failed' }, 400, origin);
    }

    // Sanitize headers against CRLF injection
    const cleanName = sanitizeHeaderValue(rawName);
    const cleanCompany = rawCompany ? sanitizeHeaderValue(rawCompany) : '';
    const cleanPhone = sanitizeHeaderValue(rawPhone);
    const cleanEmail = rawEmail.replace(/[\r\n]+/g, '').trim();

    // Email handling step based on MAIL_MODE
    const mailMode = (env.MAIL_MODE || 'log').toLowerCase();

    if (mailMode === 'log') {
      // Safe compact log: never log message body or personal details
      console.log(`[contact-worker] Consultation inquiry received in log mode at ${new Date().toISOString()}`);
      return jsonResponse({ ok: true, delivered: false }, 200, origin);
    }

    if (mailMode === 'send') {
      // Fail closed if binding is missing
      if (!env.EMAIL || typeof env.EMAIL.send !== 'function') {
        console.error('[contact-worker] EMAIL service binding not configured');
        return jsonResponse({ ok: false, error: 'Email delivery not configured' }, 502, origin);
      }

      const notifyTo = env.NOTIFY_TO;
      const mailFrom = env.MAIL_FROM;

      if (!notifyTo || !mailFrom) {
        console.error('[contact-worker] Missing NOTIFY_TO secret or MAIL_FROM var');
        return jsonResponse({ ok: false, error: 'Email routing not configured' }, 502, origin);
      }

      const subject = `New consultation request: ${cleanName}`;
      const textBody = [
        'New consultation request received from HireHR website:',
        '',
        `Name: ${cleanName}`,
        `Company: ${cleanCompany || 'N/A'}`,
        `Phone: ${cleanPhone}`,
        `Email: ${cleanEmail}`,
        '',
        'Message:',
        rawMessage
      ].join('\n');

      try {
        await env.EMAIL.send({
          to: notifyTo,
          from: mailFrom,
          replyTo: cleanEmail,
          subject,
          text: textBody
        });

        return jsonResponse({ ok: true, delivered: true }, 200, origin);
      } catch (sendErr) {
        console.error('[contact-worker] Failed to send email via EMAIL binding:', sendErr);
        return jsonResponse({ ok: false, error: 'Failed to send notification email' }, 502, origin);
      }
    }

    console.error(`[contact-worker] Unknown MAIL_MODE: ${mailMode}`);
    return jsonResponse({ ok: false, error: 'Invalid mail mode configuration' }, 500, origin);
  }
};
