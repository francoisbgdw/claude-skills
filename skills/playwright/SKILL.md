---
name: playwright
description: Browser automation with Playwright — testing, scraping, UI validation, form filling, screenshot capture. Use when automating browser interactions, testing web applications, or capturing screenshots.
allowed-tools: Bash(npx *), Bash(node *), Bash(npm *), Read, Write, Glob
---

# Browser Automation with Playwright

Generate and execute Playwright scripts on-the-fly for browser automation, testing, and validation.

## Setup

Before first use, install dependencies from the skill directory:
```bash
cd ${CLAUDE_SKILL_DIR} && npm run setup
```

This installs Playwright and the Chromium browser.

## How to automate

1. **Understand the task**: What pages, interactions, or validations are needed
2. **Write a Playwright script**: Generate a Node.js script using the Playwright API
3. **Execute via run.js**: Use the universal executor to run the script
4. **Return results**: Screenshots, console output, extracted data

### Execute a script

```bash
node ${CLAUDE_SKILL_DIR}/run.js <script-path>
```

The executor handles module resolution, browser lifecycle, and cleanup.

### Script template

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const page = await browser.newPage();

  try {
    // Navigate
    await page.goto('https://example.com');

    // Interact
    await page.fill('#username', 'user@example.com');
    await page.fill('#password', 'password');
    await page.click('button[type="submit"]');

    // Wait for result
    await page.waitForSelector('.dashboard');

    // Screenshot
    await page.screenshot({ path: '/tmp/result.png', fullPage: true });
    console.log('SUCCESS: Page loaded and screenshot captured');

    // Extract data
    const title = await page.title();
    console.log(`Page title: ${title}`);

  } catch (error) {
    await page.screenshot({ path: '/tmp/error.png' });
    console.error(`FAILED: ${error.message}`);
  } finally {
    await browser.close();
  }
})();
```

## Common patterns

### Navigate and screenshot
```javascript
await page.goto(url);
await page.waitForLoadState('networkidle');
await page.screenshot({ path: '/tmp/screenshot.png', fullPage: true });
```

### Fill forms
```javascript
await page.fill('input[name="email"]', 'user@example.com');
await page.selectOption('select#country', 'US');
await page.check('input[type="checkbox"]');
await page.click('button[type="submit"]');
```

### Wait for elements
```javascript
await page.waitForSelector('.result', { state: 'visible', timeout: 10000 });
await page.waitForURL('**/dashboard');
await page.waitForResponse(resp => resp.url().includes('/api/data'));
```

### Extract data
```javascript
const text = await page.textContent('.selector');
const items = await page.$$eval('.list-item', els => els.map(el => el.textContent));
const attr = await page.getAttribute('a.link', 'href');
```

### Handle authentication
```javascript
// Basic auth
const context = await browser.newContext({
  httpCredentials: { username: 'user', password: 'pass' }
});

// Cookie-based (set cookies before navigation)
await context.addCookies([{ name: 'session', value: 'token', domain: '.example.com', path: '/' }]);
```

### Accessibility tree (fast inspection)
```javascript
const snapshot = await page.accessibility.snapshot();
console.log(JSON.stringify(snapshot, null, 2));
```

### Multiple pages / tabs
```javascript
const [newPage] = await Promise.all([
  context.waitForEvent('page'),
  page.click('a[target="_blank"]')
]);
await newPage.waitForLoadState();
```

## Test generation

Use Playwright's codegen to record interactions:
```bash
npx playwright codegen https://example.com
```

This opens a browser and records your actions as Playwright code.

## Tips

- Use `headless: false` during development to see what's happening
- Use `slowMo: 100` to slow down actions for debugging
- Always take screenshots on errors for debugging
- Use `page.waitForLoadState('networkidle')` after navigation
- Prefer accessibility selectors (`role`, `label`) over CSS selectors for resilience
- Set timeouts appropriate to the operation (default 30s)
- Clean up `/tmp/playwright-*` files after use
