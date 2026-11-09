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
  'contact-us/index.html','partner-with-us/index.html','contract-hiring-solutions/index.html',
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

test('Contact and partnership pages use secure enquiry forms without collaboration dropdowns', () => {
  const client = read('js/main.js');
  const backend = read('worker/index.js');
  for (const page of ['contact-us/index.html', 'partner-with-us/index.html']) {
    const html = read(page);
    assert.match(html, /<form id="consultation-form"[^>]*action="\/api\/contact"/);
    for (const id of ['form-name','form-company','form-country','form-phone','form-email',
      'form-message','form-website','turnstile-widget','form-status']) {
      assert.ok(html.includes('id="' + id + '"'), page + ': Missing ' + id);
    }
    assert.ok(!html.includes('id="form-collaboration"'), page + ': Unexpected form-collaboration');
    assert.doesNotMatch(html, /form-collaboration/);
    assert.match(html, /\.\.\/js\/countries\.js/);
    assert.match(html, /challenges\.cloudflare\.com\/turnstile/);
  }
  const contactHtml = read('contact-us/index.html');
  assert.doesNotMatch(contactHtml, /How would you like to collaborate with us\?/);
  assert.match(contactHtml, /<textarea id="form-message"[^>]*required/);

  const partnerHtml = read('partner-with-us/index.html');
  assert.doesNotMatch(partnerHtml, /I am interested as/);
  assert.match(partnerHtml, /<textarea id="form-message"/);
  assert.doesNotMatch(partnerHtml, /<textarea id="form-message"[^>]*required/);
  assert.match(partnerHtml, /<h2 id="enquiry-title">Discuss a partnership<\/h2>/);

  // Backend retains optional collaboration validation for backward compatibility
  assert.match(client, /const collaboration =/);
  assert.match(client, /collaboration,\s*website,/);
  assert.match(backend, /COLLABORATION_OPTIONS\.has\(rawCollaboration\)/);
  for (const choice of choices) {
    assert.ok(backend.includes(choice), 'Backend missing: ' + choice);
  }

  const home = read('index.html');
  assert.match(home, /href="partner-with-us\/index\.html" class="nav-link">Partner with us<\/a>/);
  assert.match(home, /href="partner-with-us\/index\.html#discuss-partnership">Become a Recruitment Partner<\/a>/);
  assert.match(read('sitemap.xml'), /https:\/\/hirehrservices\.com\/partner-with-us\//);
});

test('Homepage hero copy, badge, paragraph and explore button refinements are accurate', () => {
  const home = read('index.html');
  assert.match(home, /<h1 id="home-title">Bridging Talent and Employers<br>Building Stronger Teams<\/h1>/);
  assert.doesNotMatch(home, /Bridging Talent and Employers\./);
  assert.doesNotMatch(home, /Building Stronger Teams\./);

  const expectedIntro = '<p>At HireHR Services, we connect businesses with the right talent. Based in Kolkata, we provide end-to-end recruitment solutions, helping organisations meet their hiring needs while supporting individuals in finding the right career opportunities.</p>';
  assert.ok(home.includes(expectedIntro), 'Homepage intro paragraph mismatch');

  assert.match(home, /<strong>Backed by<\/strong><span>20\+ years of expertise<\/span>/);
  assert.doesNotMatch(home, /20\+ years of experience/);

  assert.doesNotMatch(home, /Explore Our Services/);
  assert.doesNotMatch(home, /class="v2-explore"/);
});

test('About Us page and content source use updated core copy and synchronize correctly', () => {
  const aboutHtml = read('about-us/index.html');
  const pagesJson = read('content/pages.json');

  const expectedText = 'Hiring the right people is important for every business, but managing recruitment alongside daily business operations demands significant time and focus.';
  const obsoleteText = 'is not always easy';

  assert.ok(aboutHtml.includes(expectedText), 'about-us/index.html missing updated text');
  assert.ok(aboutHtml.includes('<meta name="description" content="' + expectedText + '">'));
  assert.doesNotMatch(aboutHtml, new RegExp(obsoleteText));

  assert.ok(pagesJson.includes(expectedText), 'content/pages.json missing updated text');
  assert.doesNotMatch(pagesJson, new RegExp(obsoleteText));
});

test('Hiring Expertise page displays the hero photograph with allowed CSP and no blank placeholder', () => {
  const specialtyHtml = read('our-specialty/index.html');
  const headers = read('_headers');
  const istockUrl = 'https://media.istockphoto.com/id/2158956320/photo/executive-offering-handshake-in-confident-team.jpg?s=612x612&w=0&k=20&c=eRTADCfPnhPJjXp19GxpQOKVrW_KZG_9K63bIlCRKBs=';

  assert.ok(specialtyHtml.includes(istockUrl), 'Hiring Expertise missing iStock hero photograph URL');
  assert.doesNotMatch(specialtyHtml, /class="he-hero-placeholder"/);
  assert.match(specialtyHtml, /class="he-hero-arc"[\s\S]*?<svg/);

  // Headers CSP assertions
  assert.match(headers, /img-src 'self' data: https:\/\/images\.stockcake\.com https:\/\/media\.istockphoto\.com;/);
  assert.match(headers, /https:\/\/images\.stockcake\.com/);
  assert.match(headers, /https:\/\/media\.istockphoto\.com/);
});

test('Partner With Us hero tagline presents three lines without trailing periods', () => {
  const partnerHtml = read('partner-with-us/index.html');
  assert.match(partnerHtml, /<h1 id="partner-hero-title" class="pw-hero-title">\s*Let’s Connect<br>\s*Collaborate<br>\s*<span class="pw-blue-accent">Grow Together<\/span>\s*<\/h1>/);
  assert.doesNotMatch(partnerHtml, /Let’s Connect\./);
  assert.doesNotMatch(partnerHtml, /Collaborate\./);
  assert.doesNotMatch(partnerHtml, /Grow Together\./);
});
test('All V2 inner pages use the homepage navigation model', () => {
  const innerPages = [
    'about-us/index.html','career-advice/index.html','contact-us/index.html',
    'contract-hiring-solutions/index.html','contract-to-hire-solutions/index.html',
    'job-seekers/index.html','our-specialty/index.html','permanent-hiring-solutions/index.html',
    'recruitment-process-outsourcing/index.html','partner-with-us/index.html'
  ];
  for (const page of innerPages) {
    const html = read(page);
    for (const label of ['HireHR Services','Home','About Us','Services we offer','Hiring Expertise','Partner with us','Career Support','Contact Us','Get in Touch']) {
      assert.ok(html.includes(label), page + ': missing nav/brand label ' + label);
    }
    assert.doesNotMatch(html, />EMPLOYERS</);
    assert.doesNotMatch(html, />JOB SEEKERS</);
  }
  const partner = read('partner-with-us/index.html');
  assert.match(partner, /class="partner-hero-visual"[\s\S]*?<img[^>]+https:\/\/images\.stockcake\.com\/public\/b\/0\/9\/b09b5cb5-4aa3-44fa-bec1-c210a38714a4_large\/business-handshake-close-up-stockcake\.jpg/);
  assert.doesNotMatch(partner, /class="partner-hero-visual"[\s\S]*?<svg/);
  assert.doesNotMatch(partner, /images\.(?:pexels|unsplash)\.com/);
  assert.match(read('_headers'), /img-src 'self' data: https:\/\/images\.stockcake\.com/);
});


test('Inner header geometry stays locked to the homepage grid', () => {
  const homeCss = read('css/home-v2.css');
  const innerCss = read('css/inner-v2.css');
  for (const rule of [
    'grid-template-columns:230px minmax(0,1fr) auto',
    'min-height:90px',
    'padding:10px 36px',
    'gap:24px',
    'justify-self:center',
    'gap:12px',
    'font-size:15px',
    '@media(max-width:1320px)',
    '@media(max-width:1023px)'
  ]) {
    assert.ok(homeCss.replace(/\s+/g,'').includes(rule.replace(/\s+/g,'')), 'homepage missing geometry: ' + rule);
    assert.ok(innerCss.replace(/\s+/g,'').includes(rule.replace(/\s+/g,'')), 'inner pages missing geometry: ' + rule);
  }
  assert.doesNotMatch(innerCss, /\.v2-inner-navigation\{[^}]*margin-left:auto/);
});
