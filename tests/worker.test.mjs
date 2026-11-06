const choices = [
  "Introduce companies with new recruitment requirements.",
  "I have direct access to companies looking for hiring support.",
  "I am a recruitment agency looking for recruitment delivery support for my existing clients.",
  "I want to collaborate on recruitment business and share revenue.",
  "I am interested in receiving excess recruitment requirements from HireHR Services.",
  "Other partnership opportunities."
];
import test from 'node:test';
import assert from 'node:assert/strict';
import handler from '../worker/index.js';

const valid = {
  name: 'Sample Contact', company: 'Sample Company', phone: '+91 9876543210',
  email: 'contact@example.com', message: 'Please share your recruitment offerings.',
  website: '', turnstileToken: 'unit-test-token'
};

test('Worker accepts legacy and selected partnership submissions and rejects unsafe inputs', async (t) => {
  const realFetch = globalThis.fetch;
  let verifications = 0;
  globalThis.fetch = async (url) => {
    assert.equal(url, 'https://challenges.cloudflare.com/turnstile/v0/siteverify');
    verifications++;
    return { json: async () => ({ success: true }) };
  };
  t.after(() => { globalThis.fetch = realFetch; });
  const deliveries = [];
  const env = {
    ALLOWED_ORIGINS: 'https://hirehrservices.com', MAIL_MODE: 'send',
    MAIL_FROM: 'info@hirehrservices.com', NOTIFY_TO: 'owner@example.com',
    TURNSTILE_SECRET: 'test-secret',
    EMAIL: { send: async (message) => { deliveries.push(message); } }
  };
  const submit = (payload, headers = {}) => handler.fetch(
    new Request('https://hirehrservices.com/api/contact', {
      method: 'POST',
      headers: { Origin: 'https://hirehrservices.com', 'Content-Type': 'application/json', ...headers },
      body: JSON.stringify(payload)
    }), env, {}
  );

  let response = await submit(valid);
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { ok: true, delivered: true });
  assert.equal(deliveries.length, 1);
  assert.ok(deliveries[0].text.includes('Collaboration: Not specified'));

  for (const choice of choices) {
    response = await submit({ ...valid, collaboration: choice });
    assert.equal(response.status, 200, choice);
    assert.ok(deliveries.at(-1).text.includes('Collaboration: ' + choice));
    assert.equal(deliveries.at(-1).replyTo, 'contact@example.com');
  }
  assert.equal(deliveries.length, 7);
  assert.equal(verifications, 7);

  for (const invalid of ['Not on the list', 'Revenue share\r\nBcc: attacker@example.com', 42, null]) {
    const before = verifications;
    response = await submit({ ...valid, collaboration: invalid });
    assert.equal(response.status, 400);
    assert.equal((await response.json()).error, 'Invalid collaboration option');
    assert.equal(verifications, before, 'Invalid input rejected before Turnstile');
  }
  response = await submit({ ...valid, unexpected: 'not permitted' });
  assert.equal(response.status, 400);
  response = await submit({ ...valid, website: 'https://bot.example' });
  assert.equal(response.status, 200, 'Honeypot deliberately returns success');
  assert.equal(deliveries.length, 7, 'Invalid and honeypot inputs must not deliver email');

  response = await submit({ ...valid, turnstileToken: '' });
  assert.equal(response.status, 400);
  response = await submit(valid, { Origin: 'https://evil.example' });
  assert.equal(response.status, 403);
  response = await submit(valid, { 'Content-Type': 'text/plain' });
  assert.equal(response.status, 415);
  assert.equal(deliveries.length, 7);
});
