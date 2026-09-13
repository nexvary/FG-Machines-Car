#!/usr/bin/env node
'use strict';

/**
 * FG Machines Car - Navigation Integrity Gate
 *
 * Release-blocking QA for the modern UI. It verifies:
 *  - Home / Services / About navigation by real browser clicks (English/Arabic labels supported)
 *  - every HTML page in native/ui-modern is reachable from the navigation graph
 *  - every same-origin link found on every page returns a non-error HTTP status
 *  - every unique internal page target is exercised by a real click from a source page
 *  - declared navigation buttons (data-href/data-url/data-route) navigate correctly
 *  - no javascript:/vbscript:/file: navigation links, unsafe target=_blank, page exceptions,
 *    or console errors are accepted
 *  - a machine-readable JSON report is emitted for release artifacts
 *
 * Run from PROJECT_DIR/qa/visual so Playwright resolves from that project's node_modules:
 *   FG_QA_URL=http://127.0.0.1:43890 \
 *   FG_UI_ROOT=/path/to/native/ui-modern \
 *   FG_NAV_REPORT=/path/to/report.json \
 *   node /repo/tools/navigation_integrity_gate.cjs
 */

const fs = require('fs');
const path = require('path');
const { createRequire } = require('module');
const requireFromQa = createRequire(path.join(process.cwd(), 'package.json'));
const { chromium } = requireFromQa('playwright');

const BASE = new URL(process.env.FG_QA_URL || 'http://127.0.0.1:43890/');
const UI_ROOT = process.env.FG_UI_ROOT ? path.resolve(process.env.FG_UI_ROOT) : null;
const REPORT = path.resolve(process.env.FG_NAV_REPORT || path.join(process.cwd(), 'navigation-integrity-report.json'));
const MAX_PAGES = Number(process.env.FG_NAV_MAX_PAGES || 1000);
const PAGE_TIMEOUT = Number(process.env.FG_NAV_PAGE_TIMEOUT_MS || 12000);

const badSchemes = /^(?:javascript|vbscript|file):/i;
const assetExt = /\.(?:css|js|mjs|map|png|jpe?g|gif|webp|svg|ico|woff2?|ttf|otf|mp3|mp4|webm|zip|exe|deb|dll|so|json|xml|txt)$/i;
const primaryTabs = [
  { name: 'Home', re: /^(?:home|الرئيسية|الصفحة\s*الرئيسية)$/i },
  { name: 'Services', re: /^(?:services?|الخدمات)$/i },
  { name: 'About', re: /^(?:about|about\s+us|عنا|من\s+نحن|حول(?:\s+البرنامج|\s+النظام)?)$/i },
];

function canonical(input) {
  const u = new URL(input, BASE);
  u.hash = '';
  if (u.origin !== BASE.origin) return null;
  // Keep query because routes may depend on it; normalize duplicate slashes and trailing index.html.
  u.pathname = u.pathname.replace(/\/{2,}/g, '/').replace(/\/index\.html$/i, '/');
  return u.href;
}

function hrefPath(url) {
  const u = new URL(url);
  return u.pathname + u.search;
}

function isPageUrl(url) {
  const u = new URL(url);
  return !assetExt.test(u.pathname);
}

function listHtmlFiles(root) {
  if (!root || !fs.existsSync(root)) return [];
  const out = [];
  const walk = dir => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (entry.isFile() && /\.html?$/i.test(entry.name)) {
        let rel = path.relative(root, full).split(path.sep).join('/');
        if (/^index\.html$/i.test(rel)) rel = '';
        else rel = rel.replace(/\/index\.html$/i, '/');
        out.push(canonical('/' + rel));
      }
    }
  };
  walk(root);
  return [...new Set(out.filter(Boolean))].sort();
}

async function settle(page) {
  await page.waitForSelector('body', { state: 'visible', timeout: PAGE_TIMEOUT });
  await page.waitForTimeout(80);
}

async function collectPageNavigation(page) {
  return await page.evaluate(() => {
    const visible = el => {
      const r = el.getBoundingClientRect();
      const s = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && s.display !== 'none' && s.visibility !== 'hidden';
    };
    const records = [];
    const all = [...document.querySelectorAll('a[href], button[data-href], button[data-url], button[data-route], [role="link"][data-href], [role="link"][data-url], [role="link"][data-route]')];
    for (let i = 0; i < all.length; i++) {
      const el = all[i];
      const raw = el.getAttribute('href') || el.getAttribute('data-href') || el.getAttribute('data-url') || el.getAttribute('data-route') || '';
      records.push({
        index: i,
        tag: el.tagName,
        text: (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 180),
        raw,
        href: raw ? new URL(raw, location.href).href : '',
        visible: visible(el),
        target: el.getAttribute('target') || '',
        rel: el.getAttribute('rel') || '',
        disabled: !!el.disabled || el.getAttribute('aria-disabled') === 'true',
      });
    }
    return records;
  });
}

async function navigateDirect(page, url, pageErrors, consoleErrors) {
  const localPageErrors = [];
  const localConsoleErrors = [];
  const onPageError = err => localPageErrors.push(String(err && (err.stack || err.message) || err));
  const onConsole = msg => {
    if (msg.type() === 'error') localConsoleErrors.push(msg.text());
  };
  page.on('pageerror', onPageError);
  page.on('console', onConsole);
  let response = null;
  try {
    response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: PAGE_TIMEOUT });
    await settle(page);
  } finally {
    page.off('pageerror', onPageError);
    page.off('console', onConsole);
  }
  if (localPageErrors.length) pageErrors.push({ url, errors: localPageErrors });
  // Ignore browser noise caused by an absent favicon only; everything else blocks release.
  const filtered = localConsoleErrors.filter(x => !/favicon\.ico/i.test(x));
  if (filtered.length) consoleErrors.push({ url, errors: filtered });
  return response;
}

async function clickPrimaryTab(page, tab, failures) {
  await page.goto(BASE.href, { waitUntil: 'domcontentloaded', timeout: PAGE_TIMEOUT });
  await settle(page);
  const candidates = page.locator('a,button,[role="link"],[data-route],[data-href],[data-url]');
  const count = await candidates.count();
  let found = null;
  for (let i = 0; i < count; i++) {
    const loc = candidates.nth(i);
    const text = ((await loc.innerText().catch(() => '')) || '').trim().replace(/\s+/g, ' ');
    if (!tab.re.test(text)) continue;
    if (!(await loc.isVisible().catch(() => false))) continue;
    found = loc;
    break;
  }
  if (!found) {
    failures.push(`Required primary navigation tab not found: ${tab.name}`);
    return null;
  }
  const before = canonical(page.url());
  const declared = await found.evaluate(el => el.getAttribute('href') || el.getAttribute('data-href') || el.getAttribute('data-url') || el.getAttribute('data-route') || '');
  const expected = declared ? canonical(new URL(declared, page.url()).href) : null;
  await found.click({ timeout: PAGE_TIMEOUT });
  await page.waitForLoadState('domcontentloaded', { timeout: PAGE_TIMEOUT }).catch(() => {});
  await page.waitForTimeout(100);
  const after = canonical(page.url());
  if (expected && after !== expected) failures.push(`${tab.name} click landed on ${hrefPath(after)} instead of ${hrefPath(expected)}`);
  if (!expected && after === before && tab.name !== 'Home') failures.push(`${tab.name} click did not navigate away from ${hrefPath(before)}`);
  return { name: tab.name, before, after, expected };
}

async function clickUniqueTarget(context, edge, failures) {
  const page = await context.newPage();
  try {
    await page.goto(edge.source, { waitUntil: 'domcontentloaded', timeout: PAGE_TIMEOUT });
    await settle(page);
    const selector = edge.kind === 'href'
      ? `a[href=${JSON.stringify(edge.raw)}]`
      : `[data-href=${JSON.stringify(edge.raw)}],[data-url=${JSON.stringify(edge.raw)}],[data-route=${JSON.stringify(edge.raw)}]`;
    let loc = page.locator(selector).filter({ visible: true }).first();
    if (!(await loc.count())) loc = page.locator(selector).first();
    if (!(await loc.count())) {
      failures.push(`Click source disappeared: ${hrefPath(edge.source)} -> ${hrefPath(edge.target)} (${edge.raw})`);
      return;
    }
    if (await loc.isDisabled().catch(() => false)) {
      failures.push(`Navigation control is disabled: ${hrefPath(edge.source)} -> ${hrefPath(edge.target)}`);
      return;
    }
    await loc.click({ timeout: PAGE_TIMEOUT });
    await page.waitForLoadState('domcontentloaded', { timeout: PAGE_TIMEOUT }).catch(() => {});
    await page.waitForTimeout(60);
    const actual = canonical(page.url());
    if (actual !== edge.target) failures.push(`Dead/misdirected navigation: ${hrefPath(edge.source)} -> expected ${hrefPath(edge.target)}, got ${hrefPath(actual)}`);
  } catch (err) {
    failures.push(`Click failed ${hrefPath(edge.source)} -> ${hrefPath(edge.target)}: ${err.message}`);
  } finally {
    await page.close();
  }
}

(async () => {
  fs.mkdirSync(path.dirname(REPORT), { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1366, height: 768 } });
  const page = await context.newPage();

  const failures = [];
  const pageErrors = [];
  const consoleErrors = [];
  const httpFailures = [];
  const insecureLinks = [];
  const unsafeBlankTargets = [];
  const primaryClicks = [];
  const visited = new Set();
  const discovered = new Set([canonical(BASE.href)]);
  const queue = [canonical(BASE.href)];
  const edges = [];
  const firstClickEdgeByTarget = new Map();
  const checkedHttp = new Map();

  // Explicitly click the top-level tabs requested by release policy.
  for (const tab of primaryTabs) {
    const result = await clickPrimaryTab(page, tab, failures);
    if (result) primaryClicks.push(result);
  }

  // Crawl the complete UI navigation graph from Home.
  while (queue.length) {
    const url = queue.shift();
    if (!url || visited.has(url)) continue;
    if (visited.size >= MAX_PAGES) {
      failures.push(`Navigation crawl exceeded FG_NAV_MAX_PAGES=${MAX_PAGES}`);
      break;
    }
    visited.add(url);
    const response = await navigateDirect(page, url, pageErrors, consoleErrors).catch(err => {
      failures.push(`Page failed to open ${hrefPath(url)}: ${err.message}`);
      return null;
    });
    if (response && response.status() >= 400) failures.push(`Page returned HTTP ${response.status()}: ${hrefPath(url)}`);
    if (!page.url().startsWith(BASE.origin)) {
      failures.push(`Internal page escaped application origin: ${url} -> ${page.url()}`);
      continue;
    }

    const titleAndText = await page.evaluate(() => ({ title: document.title, text: (document.body.innerText || '').trim() })).catch(() => ({ title: '', text: '' }));
    if (titleAndText.text.length < 8) failures.push(`Page appears empty/disconnected: ${hrefPath(url)}`);

    const records = await collectPageNavigation(page).catch(err => {
      failures.push(`Cannot inspect links on ${hrefPath(url)}: ${err.message}`);
      return [];
    });

    for (const rec of records) {
      if (!rec.raw || rec.raw === '#') continue;
      if (badSchemes.test(rec.raw)) {
        insecureLinks.push({ source: url, raw: rec.raw, text: rec.text });
        continue;
      }
      if (rec.target === '_blank' && !/(?:^|\s)(?:noopener|noreferrer)(?:\s|$)/i.test(rec.rel)) {
        unsafeBlankTargets.push({ source: url, raw: rec.raw, text: rec.text });
      }
      let parsed;
      try { parsed = new URL(rec.href || rec.raw, url); } catch { failures.push(`Malformed URL on ${hrefPath(url)}: ${rec.raw}`); continue; }
      if (parsed.origin !== BASE.origin) continue;
      const target = canonical(parsed.href);
      if (!target) continue;
      const kind = rec.tag === 'A' ? 'href' : 'data-route';
      edges.push({ source: url, target, raw: rec.raw, text: rec.text, kind, visible: rec.visible, disabled: rec.disabled });
      if (rec.disabled) failures.push(`Disabled internal navigation control on ${hrefPath(url)}: ${rec.text || rec.raw}`);
      discovered.add(target);
      if (isPageUrl(target) && !visited.has(target)) queue.push(target);
      if (!firstClickEdgeByTarget.has(target) && rec.visible) firstClickEdgeByTarget.set(target, { source: url, target, raw: rec.raw, kind });
    }
  }

  // Every HTML file in the UI directory must be connected to Home, not merely exist on disk.
  const diskPages = listHtmlFiles(UI_ROOT);
  const unreachable = diskPages.filter(u => !discovered.has(u) && !visited.has(u));
  for (const u of unreachable) failures.push(`Disconnected/orphan HTML page: ${hrefPath(u)}`);

  // Check every same-origin link found on every page at HTTP level, including duplicates by edge report.
  for (const edge of edges) {
    if (checkedHttp.has(edge.target)) continue;
    try {
      const r = await context.request.get(edge.target, { failOnStatusCode: false, timeout: PAGE_TIMEOUT });
      checkedHttp.set(edge.target, r.status());
      if (r.status() >= 400) httpFailures.push({ url: edge.target, status: r.status() });
    } catch (err) {
      checkedHttp.set(edge.target, 0);
      httpFailures.push({ url: edge.target, status: 0, error: err.message });
    }
  }

  // Real-click every unique internal destination at least once from a page that exposes it.
  // This catches dead handlers where a URL exists in markup but clicking does nothing.
  for (const [target, edge] of firstClickEdgeByTarget) {
    if (!isPageUrl(target)) continue;
    await clickUniqueTarget(context, edge, failures);
  }

  if (insecureLinks.length) failures.push(`Unsafe navigation schemes found: ${insecureLinks.length}`);
  if (unsafeBlankTargets.length) failures.push(`target=_blank links without rel=noopener/noreferrer: ${unsafeBlankTargets.length}`);
  if (httpFailures.length) failures.push(`Broken internal HTTP links: ${httpFailures.length}`);
  if (pageErrors.length) failures.push(`Unhandled page exceptions: ${pageErrors.length}`);
  if (consoleErrors.length) failures.push(`Browser console errors: ${consoleErrors.length}`);

  const report = {
    gate: 'Navigation Integrity Gate',
    baseUrl: BASE.href,
    uiRoot: UI_ROOT,
    generatedAt: new Date().toISOString(),
    summary: {
      pass: failures.length === 0,
      primaryTabsClicked: primaryClicks.length,
      htmlFilesOnDisk: diskPages.length,
      pagesVisited: visited.size,
      internalLinkOccurrences: edges.length,
      uniqueInternalTargets: checkedHttp.size,
      uniqueTargetsClicked: [...firstClickEdgeByTarget.keys()].filter(isPageUrl).length,
      orphanPages: unreachable.length,
      brokenHttpLinks: httpFailures.length,
      unsafeSchemes: insecureLinks.length,
      unsafeBlankTargets: unsafeBlankTargets.length,
      pageExceptionPages: pageErrors.length,
      consoleErrorPages: consoleErrors.length,
      failures: failures.length,
    },
    primaryClicks,
    unreachable,
    httpFailures,
    insecureLinks,
    unsafeBlankTargets,
    pageErrors,
    consoleErrors,
    failures,
  };
  fs.writeFileSync(REPORT, JSON.stringify(report, null, 2));
  await page.close();
  await browser.close();

  console.log('NAVIGATION_INTEGRITY_GATE_REPORT', REPORT);
  console.log(JSON.stringify(report.summary));
  if (failures.length) {
    console.error('NAVIGATION_INTEGRITY_GATE_FAIL');
    for (const f of failures.slice(0, 100)) console.error(' - ' + f);
    process.exit(1);
  }
  console.log(`NAVIGATION_INTEGRITY_GATE_PASS pages=${visited.size} links=${edges.length} uniqueTargets=${checkedHttp.size} clicked=${report.summary.uniqueTargetsClicked}`);
})().catch(err => {
  try {
    fs.mkdirSync(path.dirname(REPORT), { recursive: true });
    fs.writeFileSync(REPORT, JSON.stringify({ gate: 'Navigation Integrity Gate', pass: false, fatal: String(err.stack || err) }, null, 2));
  } catch {}
  console.error(err.stack || err);
  process.exit(1);
});
