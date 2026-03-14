#!/usr/bin/env node

/**
 * Universal Playwright script executor.
 * Handles module resolution so generated scripts can require('playwright') reliably.
 *
 * Usage: node run.js <script-path>
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const scriptPath = process.argv[2];

if (!scriptPath) {
  console.error('Usage: node run.js <script-path>');
  process.exit(1);
}

const resolvedScript = path.resolve(scriptPath);

if (!fs.existsSync(resolvedScript)) {
  console.error(`Script not found: ${resolvedScript}`);
  process.exit(1);
}

// Set NODE_PATH so the script can resolve playwright from this skill's node_modules
const skillDir = __dirname;
const nodeModulesPath = path.join(skillDir, 'node_modules');

const env = {
  ...process.env,
  NODE_PATH: nodeModulesPath,
};

try {
  execSync(`node "${resolvedScript}"`, {
    env,
    stdio: 'inherit',
    timeout: 120000, // 2 minute timeout
  });
} catch (error) {
  if (error.status) {
    process.exit(error.status);
  }
  console.error(`Execution failed: ${error.message}`);
  process.exit(1);
}
