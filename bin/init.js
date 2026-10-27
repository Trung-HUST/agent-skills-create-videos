#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const targetDir = process.cwd();
const rootDir = path.join(__dirname, '..');

const ITEMS_TO_COPY = [
  '.agents',
  'AGENTS.md',
  'GEMINI.md',
  'CLAUDE.md',
  'copilot-instructions.md'
];

function copyRecursiveSync(from, to) {
  const stat = fs.lstatSync(from);
  if (stat.isDirectory()) {
    if (!fs.existsSync(to)) {
      fs.mkdirSync(to, { recursive: true });
    }
    for (const element of fs.readdirSync(from)) {
      copyRecursiveSync(path.join(from, element), path.join(to, element));
    }
  } else if (stat.isFile()) {
    fs.mkdirSync(path.dirname(to), { recursive: true });
    fs.copyFileSync(from, to);
  }
}

console.log('Initializing agent-skills-create-videos...');

try {
  for (const item of ITEMS_TO_COPY) {
    const src = path.join(rootDir, item);
    const dest = path.join(targetDir, item);
    if (fs.existsSync(src)) {
      copyRecursiveSync(src, dest);
      console.log(`Installed: ${item}`);
    }
  }
  console.log('Initialization complete! AI Video Production skills and memory are ready.');
} catch (error) {
  console.error('Error initializing agent-skills-create-videos:', error);
  process.exit(1);
}
