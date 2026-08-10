const {
  existsSync,
  lstatSync,
  mkdirSync,
  readdirSync,
  realpathSync,
  statSync,
  writeFileSync,
} = require('node:fs');
const { createHash } = require('node:crypto');
const { relative, resolve, sep } = require('node:path');
const { spawnSync } = require('node:child_process');

const required = [
  'CHAT_HISTORY_EVAL_ROOT',
  'CHAT_HISTORY_EVAL_CURRENT_SKILL_WORKSPACE',
  'CHAT_HISTORY_EVAL_BASELINE_WORKSPACE',
  'CHAT_HISTORY_EVAL_CODEX_HOME',
  'CHAT_HISTORY_EVAL_HOME',
];

const missing = required.filter((name) => !process.env[name]);
if (missing.length) {
  console.error(`Set ${missing.join(', ')} before running this controlled evaluation.`);
  process.exit(1);
}

const directories = Object.fromEntries(
  required.map((name) => [name, resolve(process.env[name])]),
);
for (const [name, target] of Object.entries(directories)) {
  if (!existsSync(target) || !statSync(target).isDirectory()) {
    console.error(`${name} must name an existing directory: ${target}`);
    process.exit(1);
  }
  directories[name] = realpathSync(target);
}

const harnessDir = realpathSync(resolve(__dirname, '..'));
const repoRoot = realpathSync(resolve(__dirname, '..', '..', '..'));
const resultRoot = directories.CHAT_HISTORY_EVAL_ROOT;
const resultRelative = relative(repoRoot, resultRoot);
if (!resultRelative || (!resultRelative.startsWith(`..${sep}`) && resultRelative !== '..')) {
  console.error('CHAT_HISTORY_EVAL_ROOT must be outside the repository so trajectories stay out of git.');
  process.exit(1);
}

const currentSkill = resolve(
  directories.CHAT_HISTORY_EVAL_CURRENT_SKILL_WORKSPACE,
  '.agents',
  'skills',
  'chat-history',
);
const baselineSkill = resolve(
  directories.CHAT_HISTORY_EVAL_BASELINE_WORKSPACE,
  '.agents',
  'skills',
  'chat-history',
);
const profile = resolve(
  directories.CHAT_HISTORY_EVAL_CODEX_HOME,
  'agents',
  'chat-history-researcher.toml',
);
const sharedHomeSkill = resolve(
  directories.CHAT_HISTORY_EVAL_HOME,
  '.agents',
  'skills',
  'chat-history',
);
const codexHomeSkill = resolve(
  directories.CHAT_HISTORY_EVAL_CODEX_HOME,
  'skills',
  'chat-history',
);
if (!existsSync(currentSkill) || !statSync(currentSkill).isDirectory()) {
  console.error(`CHAT_HISTORY_EVAL_CURRENT_SKILL_WORKSPACE is missing .agents/skills/chat-history.`);
  process.exit(1);
}
for (const unexpected of [baselineSkill, sharedHomeSkill, codexHomeSkill]) {
  if (existsSync(unexpected)) {
    console.error(`The no-skill condition is contaminated by chat-history at ${unexpected}.`);
    process.exit(1);
  }
}
if (!existsSync(profile) || !statSync(profile).isFile()) {
  console.error(`CHAT_HISTORY_EVAL_CODEX_HOME is missing agents/chat-history-researcher.toml.`);
  process.exit(1);
}

const promptfoo = resolve(
  harnessDir,
  'node_modules',
  '.bin',
  process.platform === 'win32' ? 'promptfoo.cmd' : 'promptfoo',
);
if (!existsSync(promptfoo)) {
  console.error('The pinned local Promptfoo binary is missing. Run npm ci in evals/harness first.');
  process.exit(1);
}

function hashFile(path) {
  return createHash('sha256').update(require('node:fs').readFileSync(path)).digest('hex');
}

function hashTree(root) {
  const hash = createHash('sha256');
  const files = [];
  function visit(directory) {
    for (const entry of readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      const path = resolve(directory, entry.name);
      const relativePath = relative(root, path).replaceAll('\\', '/');
      if (entry.isDirectory()) {
        visit(path);
      } else if (entry.isFile()) {
        const content = require('node:fs').readFileSync(path);
        hash.update(`file:${relativePath}\0`);
        hash.update(content);
        files.push({ path: relativePath, sha256: createHash('sha256').update(content).digest('hex') });
      } else if (lstatSync(path).isSymbolicLink()) {
        throw new Error(`Refusing to fingerprint symbolic link in evaluated skill: ${path}`);
      }
    }
  }
  visit(root);
  return { sha256: hash.digest('hex'), files };
}

mkdirSync(resultRoot, { recursive: true });
writeFileSync(resolve(resultRoot, 'run-manifest.json'), `${JSON.stringify({
  schema_version: 1,
  created_at: new Date().toISOString(),
  harness_config_sha256: hashFile(resolve(harnessDir, 'promptfooconfig.yaml')),
  current_skill: hashTree(currentSkill),
  chat_history_researcher_profile_sha256: hashFile(profile),
  conditions: ['current-skill', 'no-skill-baseline'],
  trials_per_scenario_per_condition: 3,
}, null, 2)}\n`);

const child = spawnSync(
  promptfoo,
  ['eval', '-c', 'promptfooconfig.yaml', '--no-cache', '-o', resolve(resultRoot, 'results.json')],
  { cwd: harnessDir, stdio: 'inherit' },
);

process.exit(child.status ?? 1);
