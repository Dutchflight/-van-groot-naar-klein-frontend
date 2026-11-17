// Leest actuele civiele-techniek-opdrachten van Freelance.nl via een gewone browserweergave (Playwright).
// Gebruik: node vacatures/tools/freelance_nl.mjs > opdrachten.json
// Per opdracht: titel, plaats, uren, status (Gepubliceerd/Gearchiveerd), publicatiedatum, link.
// Sluitingsdatum en tarief toont Freelance.nl alleen na inloggen.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';

const LIJST = 'https://www.freelance.nl/opdrachten/civiele-techniek';
const browser = await chromium.launch({ args: ['--no-sandbox'] });
const page = await browser.newPage();
page.setDefaultTimeout(30000);
// alleen tekst laden: afbeeldingen, lettertypen, media en externe trackers overslaan
await page.route('**/*', r => {
  const req = r.request();
  const extern = !req.url().startsWith('https://www.freelance.nl');
  return (extern || ['image', 'font', 'media'].includes(req.resourceType())) ? r.abort() : r.continue();
});
const links = new Set();
// de lijst toont de 15 nieuwste opdrachten; wekelijks bijhouden is daarmee genoeg
await page.goto(LIJST, { waitUntil: 'domcontentloaded', timeout: 30000 });
await page.waitForSelector('a[href*="/opdracht/"]', { timeout: 30000 }).catch(() => {});
// alleen projectleiding openen (titel uit de lijst), om de site niet onnodig te belasten
const ROL = /project ?leid|project ?manag|programma ?manag|projectdirect|kwartiermaker/i;
(await page.$$eval('a[href*="/opdracht/"]', as => as.map(a => [a.href.split('?')[0], a.innerText])))
  .filter(([, tekst]) => ROL.test(tekst)).forEach(([h]) => links.add(h));
const uit = [];
for (const url of links) {
  const t0 = Date.now(); console.error('>', url);
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForSelector('text=Publicatiedatum', { timeout: 30000 });
    const t = (await page.innerText('main').catch(() => page.innerText('body'))).replace(/\s+/g, ' ');
    const veld = (k, stop) => (t.match(new RegExp(k + ':\\s*(.+?)\\s+(?:' + stop + ')')) || [])[1] || '';
    const titel = (await page.$eval('h1', h => h.innerText).catch(() => '')).trim();
    uit.push({
      titel, url,
      status: veld('Status', 'Publicatiedatum'),
      geplaatst: veld('Publicatiedatum', 'Weergaven'),
      plaats: veld('Op locatie', 'FTE|Opdrachtomschrijving'),
      uren: (t.match(/FTE:\s*([\d\s–-]+)\s*uur/) || [])[1]?.trim() || '',
    });
  } catch (e) { console.error('  fout', String(e).slice(0, 120)); /* opdracht net offline: overslaan */ }
  console.error('  ', Date.now() - t0, 'ms');
  await page.waitForTimeout(2000);
}
console.log(JSON.stringify(uit));
await browser.close();
