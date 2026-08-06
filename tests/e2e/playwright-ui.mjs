import { chromium } from 'playwright';

const base = process.env.RESUME_TAILOR_URL || 'http://127.0.0.1:8765';
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
const jd = 'Backend SWE role using Go, TypeScript, React, AWS, Docker, Kubernetes, Redis, REST APIs, and CI/CD.';
const name = `playwright-backend-${Date.now()}`;

await page.goto(base, { waitUntil: 'domcontentloaded' });
await page.getByRole('textbox').fill(jd);
await page.getByRole('button', { name: /Generate New PDF/ }).click();
await page.getByRole('link', { name: 'Open PDF' }).waitFor();
let text = await page.locator('body').innerText();
if (!text.includes('PDF generated: 1 page')) throw new Error('PDF page validation missing');
if (!text.includes('Redis')) throw new Error('safe suggestion missing');
const diffHref = await page.getByRole('link', { name: 'Diff' }).getAttribute('href');
if (diffHref !== '/files/tailored.diff') throw new Error('diff link missing');

await page.getByPlaceholder('backend-go-vault').fill(name);
await page.getByRole('button', { name: 'Save to Library' }).click();
await page.getByText(`Saved ${name}.`).waitFor();
await page.goto(base, { waitUntil: 'domcontentloaded' });
await page.getByRole('textbox').fill(jd);
await page.getByRole('button', { name: /Find Existing Resume/ }).click();
await page.getByRole('link', { name: 'Open PDF' }).first().waitFor();
text = await page.locator('body').innerText();
if (!text.includes(name)) throw new Error('saved resume missing from matches');
if (!text.includes('Generate New PDF Instead')) throw new Error('fallback generate action missing');

await page.goto(`${base}/library`, { waitUntil: 'domcontentloaded' });
await page.locator('tr', { hasText: name }).getByRole('button', { name: 'Delete' }).click();
await page.getByText('Deleted resume.').waitFor();
text = await page.locator('body').innerText();
if (text.includes(name)) throw new Error('test resume cleanup failed');

console.log('playwright ui library smoke: ok');
await browser.close();
