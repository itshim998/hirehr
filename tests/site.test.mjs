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
import { readFileSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = (p) => readFileSync(resolve(root, p), 'utf8');
const pages = [
  'index.html','404.html','about-us/index.html','career-advice/index.html',
  'contact-us/index.html','contract-hiring-solutions/index.html',
  'contract-to-hire-solutions/index.html','job-seekers/index.html',
  'our-specialty/index.html','permanent-hiring-solutions/index.html',
  'recruitment-process-outsourcing/index.html'
];

test('Retired service is absent from public pages, navigation and sitemap', () => {
  for (const page of pages) assert.doesNotMatch(read(page), /background[\s-]*verification/i, page);
  assert.doesNotMatch(read('sitemap.xml'), /background[\s-]*verification/i);
  assert.equal(existsSync(resolve(root, 'background-verification-service/index.html')), false);
});

test('All internal links from public pages resolve', () => {
  for (const page of pages) {
    for (const match of read(page).matchAll(/<a\b[^>]*\bhref="([^"]+)"/g)) {
      const href = match[1].split('#')[0].split('?')[0];
      if (!href || /^(?:[a-z]+:|\/\/)/i.test(href)) continue;
      const resolved = resolve(root, dirname(page), href);
      assert.ok(existsSync(resolved), page + ': broken internal link ' + href);
    }
  }
});

test('Contact page has six exact partnership choices and secure form wiring', () => {
  const html = read('contact-us/index.html');
  const client = read('js/main.js');
  const backend = read('worker/index.js');
  assert.match(html, /<form id="consultation-form"/);
  for (const id of ['form-name','form-company','form-country','form-phone','form-email',
    'form-collaboration','form-message','form-website','turnstile-widget','form-status']) {
    assert.ok(html.includes('id="' + id + '"'), 'Missing ' + id);
  }
  const dropdown = html.match(/<select id="form-collaboration"[\s\S]*?<\/select>/);
  assert.ok(dropdown);
  assert.equal([...dropdown[0].matchAll(/<option\b/g)].length, 7, 'Placeholder plus 6 choices');
  for (const choice of choices) {
    assert.ok(dropdown[0].includes('value="' + choice + '">' + choice + '</option>'), choice);
    assert.ok(backend.includes(choice), 'Backend missing: ' + choice);
  }
  assert.match(html, /\.\.\/js\/countries\.js/);
  assert.match(html, /challenges\.cloudflare\.com\/turnstile/);
  assert.match(client, /const collaboration =/);
  assert.match(client, /collaboration,\s*website,/);
  assert.match(backend, /COLLABORATION_OPTIONS\.has\(rawCollaboration\)/);
  assert.match(read('index.html'), /<strong>Backed by<\/strong><span>20\+ years of experience<\/span>/);
});
