#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { createRequire } = require('module');
const requireFromQa = createRequire(path.join(process.cwd(), 'package.json'));
const { chromium } = requireFromQa('playwright');

const BASE = process.env.FG_QA_URL || 'http://127.0.0.1:43890';
const OUT = path.resolve(process.env.FG_LAPTOP_OUT || process.cwd());
const PREFIX = process.env.FG_LAPTOP_PREFIX || 'FG-Machines-Car-Windows';

function gateInPage() {
  const main = document.querySelector('main,.main-content,.workspace-content,.page-content,.content');
  const sidebar = document.querySelector('.fg-v3-sidebar,aside,.sidebar,[class*="sidebar"]');
  const visible = el => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 1 && r.height > 1 && s.display !== 'none' && s.visibility !== 'hidden';
  };
  const candidates = main ? [...main.querySelectorAll('.fg-ornate-frame,.card,.panel,section,article,[class*="card"]')] : [];
  const sparse = [];
  for (const el of candidates) {
    if (!visible(el)) continue;
    if (el.parentElement && candidates.includes(el.parentElement)) continue;
    const r = el.getBoundingClientRect();
    if (r.height < 300) continue;
    let contentBottom = r.top;
    const nodes = [...el.querySelectorAll('*')].filter(n =>
      visible(n) && !n.matches('.fg-corner,.fg-crest,.fg-header-crest') &&
      !n.closest('.fg-corner,.fg-crest,.fg-header-crest'));
    for (const n of nodes) {
      const nr = n.getBoundingClientRect();
      if (n.textContent.trim() || ['BUTTON','A','INPUT','SELECT','TEXTAREA','TABLE','CANVAS','SVG','IMG'].includes(n.tagName)) {
        contentBottom = Math.max(contentBottom, nr.bottom);
      }
    }
    const waste = Math.max(0, r.bottom - contentBottom);
    if (r.height > 330 && waste > 170) sparse.push({ h: Math.round(r.height), waste: Math.round(waste), cls: String(el.className).slice(0, 120) });
  }
  return {
    vw: innerWidth,
    vh: innerHeight,
    bodyW: document.body.scrollWidth,
    bodyH: document.body.scrollHeight,
    main: main ? { clientHeight: main.clientHeight, scrollHeight: main.scrollHeight, overflowY: getComputedStyle(main).overflowY } : null,
    sidebar: sidebar ? { clientHeight: sidebar.clientHeight, scrollHeight: sidebar.scrollHeight } : null,
    sparse,
  };
}

async function validate(page, label) {
  const fit = await page.evaluate(gateInPage);
  console.log(label, JSON.stringify(fit));
  if (fit.vw !== 1366 || fit.vh !== 768) throw new Error(`${label}: wrong viewport`);
  if (fit.bodyW > fit.vw + 4) throw new Error(`${label}: horizontal clipping ${fit.bodyW}/${fit.vw}`);
  if (!fit.main) throw new Error(`${label}: main content not found`);
  if (!['auto', 'scroll'].includes(fit.main.overflowY)) throw new Error(`${label}: main not scrollable`);
  if (fit.sparse.length) throw new Error(`${label}: stretched sparse panels ${JSON.stringify(fit.sparse.slice(0, 4))}`);
  await page.evaluate(() => {
    const m = document.querySelector('main,.main-content,.workspace-content,.page-content,.content');
    if (m) m.scrollTop = m.scrollHeight;
  });
  await page.waitForTimeout(120);
  const bottomReachable = await page.evaluate(() => {
    const m = document.querySelector('main,.main-content,.workspace-content,.page-content,.content');
    return !m || (m.scrollTop + m.clientHeight >= m.scrollHeight - 6);
  });
  if (!bottomReachable) throw new Error(`${label}: bottom content not reachable`);
  await page.evaluate(() => {
    const m = document.querySelector('main,.main-content,.workspace-content,.page-content,.content');
    if (m) m.scrollTop = 0;
  });
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1366, height: 768 } });

  await page.goto(BASE + '/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForSelector('body', { state: 'visible', timeout: 10000 });
  await page.waitForTimeout(800);
  await validate(page, 'LAPTOP_HOME');
  const homeShot = path.join(OUT, `${PREFIX}-Laptop-R4-1366x768.png`);
  await page.screenshot({ path: homeShot, fullPage: false });

  const first = page.locator('main a[href*="modules"],main a[href*="m0"],.module-card a,.card a').first();
  if (await first.count()) {
    await first.click();
    await page.waitForTimeout(500);
  } else {
    await page.goto(BASE + '/modules/m001.html', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForSelector('body', { state: 'visible', timeout: 10000 });
  }
  await validate(page, 'LAPTOP_MODULE');
  const moduleShot = path.join(OUT, `${PREFIX}-Module-R4-1366x768.png`);
  await page.screenshot({ path: moduleShot, fullPage: false });

  if (!fs.existsSync(homeShot) || !fs.existsSync(moduleShot)) throw new Error('Laptop-fit screenshots missing');
  await browser.close();
  console.log(`LAPTOP_FIT_GATE_PASS home=${homeShot} module=${moduleShot}`);
})().catch(err => {
  console.error(err.stack || err);
  process.exit(1);
});
