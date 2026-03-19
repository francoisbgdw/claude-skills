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

## Element ref system (accessibility-first)

Instead of guessing fragile CSS selectors, use the accessibility tree to discover elements and interact via role-based locators. This is more robust against DOM changes, React hydration, and Shadow DOM.

### Step 1: Snapshot the accessibility tree

```javascript
// Get the full accessibility tree with roles and names
const snapshot = await page.accessibility.snapshot();
console.log(JSON.stringify(snapshot, null, 2));
```

This returns a tree of elements with their roles (button, link, textbox, heading, etc.) and accessible names.

### Step 2: Use role-based locators (preferred)

```javascript
// Instead of: page.click('button.submit-btn')
// Use:
await page.getByRole('button', { name: 'Submit' }).click();

// Instead of: page.fill('input#email')
// Use:
await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');

// Instead of: page.click('a.nav-link')
// Use:
await page.getByRole('link', { name: 'Dashboard' }).click();

// Instead of: page.click('input[type="checkbox"]')
// Use:
await page.getByRole('checkbox', { name: 'Remember me' }).check();
```

### Step 3: Locator priority (most to least robust)

1. **`getByRole`** — uses ARIA roles and accessible names. Most resilient to DOM changes.
2. **`getByLabel`** — finds form inputs by their associated label text.
3. **`getByPlaceholder`** — finds inputs by placeholder text.
4. **`getByText`** — finds elements by visible text content.
5. **`getByTestId`** — finds elements by `data-testid` attribute (requires app support).
6. **CSS selectors** — last resort. Fragile, breaks on refactors.

### Interactive element discovery

When you don't know what elements are on the page, take a snapshot first:

```javascript
// Discover all interactive elements
const snapshot = await page.accessibility.snapshot();

function listInteractive(node, depth = 0) {
  const interactive = ['button', 'link', 'textbox', 'checkbox', 'radio',
                        'combobox', 'menuitem', 'tab', 'switch'];
  if (interactive.includes(node.role)) {
    console.log(`${'  '.repeat(depth)}[${node.role}] "${node.name}"`);
  }
  if (node.children) {
    for (const child of node.children) {
      listInteractive(child, depth + 1);
    }
  }
}

listInteractive(snapshot);
```

Output example:
```
[link] "Home"
[link] "Dashboard"
[textbox] "Search"
[button] "Submit"
[checkbox] "Remember me"
```

Then interact using the discovered roles and names:
```javascript
await page.getByRole('link', { name: 'Dashboard' }).click();
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
await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
await page.getByRole('combobox', { name: 'Country' }).selectOption('US');
await page.getByRole('checkbox', { name: 'Terms' }).check();
await page.getByRole('button', { name: 'Submit' }).click();
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

### Multiple pages / tabs
```javascript
const [newPage] = await Promise.all([
  context.waitForEvent('page'),
  page.click('a[target="_blank"]')
]);
await newPage.waitForLoadState();
```

## Persistent browser pattern

For multi-step workflows that require many browser interactions, keep the browser alive across commands instead of cold-starting each time:

```javascript
const { chromium } = require('playwright');

// Launch once, reuse across interactions
const browser = await chromium.launch({ headless: false });
const context = await browser.newContext();
const page = await context.newPage();

// ... perform multiple interactions without closing ...

// Only close when fully done
await browser.close();
```

When writing multi-step automation scripts, structure them as a single script with sequential steps rather than launching/closing the browser for each step. This is faster and preserves state (cookies, localStorage, session).

## Test generation

Use Playwright's codegen to record interactions:
```bash
npx playwright codegen https://example.com
```

This opens a browser and records your actions as Playwright code.

## Tips

- Prefer role-based locators (`getByRole`, `getByLabel`) over CSS selectors for resilience
- Use the accessibility tree snapshot to discover elements before writing selectors
- Use `headless: false` during development to see what's happening
- Use `slowMo: 100` to slow down actions for debugging
- Always take screenshots on errors for debugging
- Use `page.waitForLoadState('networkidle')` after navigation
- Set timeouts appropriate to the operation (default 30s)
- Clean up `/tmp/playwright-*` files after use
- For multi-step workflows, use a single script to avoid cold-start overhead
