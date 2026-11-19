// Rapid-alert watcher: checks the official sources players need RIGHT NOW and prints what changed
// since the last run. Cheap (no AI agents). State in page/watch-state.json.
// Usage: node tools/watch_official.js   → prints "NO CHANGES" or a list of changes.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const STATE = path.join(__dirname, '..', 'page', 'watch-state.json');
const SOURCES = [
  { id: 'rockstar-newswire', url: 'https://www.rockstargames.com/newswire', links: '/newswire/article/', pick: (t) => lines(t).slice(0, 10) },
  { id: 'gta6-media-artwork', url: 'https://www.rockstargames.com/VI/media/artwork-wallpapers', pick: (t) => lines(t).filter((l) => /map|poster|postcard|wallpaper|cover/i.test(l)).slice(0, 40) },
  { id: 'gta6-home', url: 'https://www.rockstargames.com/VI', pick: (t) => lines(t).filter((l) => /COMING|AVAILABLE|OUT NOW|PRE-LOAD|PRE-ORDER|BUY|PLAY NOW/i.test(l) && !/^NOVEMBER 19, 2026$/i.test(l)).sort().slice(0, 8) },
  { id: 'ps5-system-software', url: 'https://www.playstation.com/en-us/support/hardware/ps5/system-software-info/', pick: (t) => lines(t).filter((l) => /^Version|\d{2}\.\d{2}-\d{2}\.\d{2}/.test(l)).slice(0, 3) },
  { id: 'rockstar-support-status', url: 'https://support.rockstargames.com/servicestatus', pick: (t) => lines(t).filter((l) => /PlayStation|Xbox|Social Club|Grand Theft Auto VI|Up|Down|Limited|Online/i.test(l)).slice(0, 20) },
  { id: 'xbox-wire-rss', url: 'https://news.xbox.com/en-us/feed/', raw: true, pick: (t) => rssTitles(t).filter((l) => /Grand Theft Auto|GTA/i.test(l)).slice(0, 8) },
  { id: 'ps-blog-rss', url: 'https://blog.playstation.com/feed/', raw: true, pick: (t) => rssTitles(t).filter((l) => /Grand Theft Auto|GTA/i.test(l)).slice(0, 8) },
];

function lines(t) { return [...new Set(t.split('\n').map((s) => s.trim()).filter((s) => s.length > 2 && s.length < 200))]; }
function rssTitles(xml) { return [...xml.matchAll(/<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?<\/title>/g)].map((m) => m[1]); }

(async () => {
  const prev = fs.existsSync(STATE) ? JSON.parse(fs.readFileSync(STATE, 'utf8')) : {};
  const next = {}; const changes = []; const errors = [];
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const s of SOURCES) {
    try {
      let text;
      if (s.raw) {
        const r = await fetch(s.url, { headers: { 'User-Agent': 'fullclear-watch/1.0' } });
        if (!r.ok) throw new Error('HTTP ' + r.status);
        text = await r.text();
      } else {
        await page.goto(s.url, { waitUntil: s.links ? 'networkidle' : 'domcontentloaded', timeout: 60000 });
        await page.waitForTimeout(4000);
        text = s.links
          ? await page.evaluate((sel) => [...document.querySelectorAll(`a[href*="${sel}"]`)].map((a) => a.innerText.replace(/\s+/g, ' ').trim()).join('\n'), s.links)
          : await page.evaluate(() => document.body.innerText);
      }
      const items = s.pick(text);
      next[s.id] = items;
      const old = prev[s.id] || [];
      const added = items.filter((i) => !old.includes(i));
      const removed = old.filter((i) => !items.includes(i));
      if (prev[s.id] && (added.length || removed.length)) changes.push({ source: s.id, url: s.url, added, removed });
    } catch (e) {
      errors.push(`${s.id}: ${e.message.slice(0, 80)}`);
      next[s.id] = prev[s.id] || [];
    }
  }
  await browser.close();
  fs.writeFileSync(STATE, JSON.stringify(next, null, 1));
  if (!changes.length) console.log('NO CHANGES');
  for (const c of changes) {
    console.log(`CHANGE in ${c.source} (${c.url})`);
    c.added.forEach((a) => console.log('  + ' + a));
    c.removed.forEach((r) => console.log('  - ' + r));
  }
  if (errors.length) console.log('UNREACHABLE: ' + errors.join(' | '));
})();
