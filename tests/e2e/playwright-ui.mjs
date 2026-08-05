import { chromium } from 'playwright';

const base = process.env.RESUME_TAILOR_URL || 'http://127.0.0.1:8765';
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await page.goto(base, { waitUntil: 'domcontentloaded' });
await page.getByRole('textbox').fill('Backend SWE role using Go, TypeScript, React, AWS, Docker, Kubernetes, Redis, REST APIs, and CI/CD.');
await page.getByRole('button', { name: /Tailor Resume/ }).click();
await page.getByRole('link', { name: 'Open PDF' }).waitFor();
const text = await page.locator('body').innerText();
if (!text.includes('PDF generated: 1 page')) throw new Error('PDF page validation missing');
if (!text.includes('Redis')) throw new Error('safe suggestion missing');
const diffHref = await page.getByRole('link', { name: 'Diff' }).getAttribute('href');
if (diffHref !== '/files/tailored.diff') throw new Error('diff link missing');
console.log('playwright ui smoke: ok');
await browser.close();
