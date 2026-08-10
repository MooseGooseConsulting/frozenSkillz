const { existsSync, mkdirSync, statSync } = require('node:fs');
const { relative, resolve, sep } = require('node:path');
const { spawnSync } = require('node:child_process');

const required = [
  'CHAT_HISTORY_EVAL_ROOT',
  'CHAT_HISTORY_EVAL_CURRENT_SKILL_WORKSPACE',
  'CHAT_HISTORY_EVAL_BASELINE_WORKSPACE',
  'CHAT_HISTORY_EVAL_CODEX_HOME',
];

const missing = required.filter((name) => !process.env[name]);
if (missing.length) {
  console.error(`Set ${missing.join(', ')} before running this controlled evaluation.`);
  process.exit(1);
}

for (const name of required) {
  const target = resolve(process.env[name]);
  if (!existsSync(target) || !statSync(target).isDirectory()) {
    console.error(`${name} must name an existing directory: ${target}`);
    process.exit(1);
  }
}

const harnessDir = resolve(__dirname, '..');
const resultRoot = resolve(process.env.CHAT_HISTORY_EVAL_ROOT);
const resultRelative = relative(harnessDir, resultRoot);
if (!resultRelative || (!resultRelative.startsWith(`..${sep}`) && resultRelative !== '..')) {
  console.error('CHAT_HISTORY_EVAL_ROOT must be outside evals/harness so trajectories stay out of git.');
  process.exit(1);
}

mkdirSync(resultRoot, { recursive: true });
const output = resolve(resultRoot, 'results.json');
const command = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const child = spawnSync(
  command,
  ['promptfoo', 'eval', '-c', 'promptfooconfig.yaml', '--no-cache', '-o', output],
  { cwd: harnessDir, stdio: 'inherit' },
);

process.exit(child.status ?? 1);
