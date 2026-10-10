import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname, resolve, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { parse } from 'acorn';

const hash = (text) => createHash('sha256').update(text).digest('hex');
const ast = (code) => parse(code, { ecmaVersion: 'latest', sourceType: 'module', allowAwaitOutsideFunction: true });
const layerName = (name) => /^[a-z][A-Za-z0-9_]*$/.test(name) && !name.endsWith('_');
const stemName = (name) => typeof name === 'string' && /^[a-z][a-z0-9_-]*$/.test(name) && name !== 'master';

function bindings(node) {
  if (!node) return [];
  if (node.type === 'Identifier') return [node.name];
  if (node.type === 'RestElement') return bindings(node.argument);
  if (node.type === 'AssignmentPattern') return bindings(node.left);
  if (node.type === 'ArrayPattern') return node.elements.flatMap(bindings);
  if (node.type === 'ObjectPattern') return node.properties.flatMap((p) => bindings(p.type === 'RestElement' ? p.argument : p.value));
  return [];
}

export function validateModules(modules) {
  const labels = new Set();
  const declarations = new Set();
  const stems = {};
  let tempoCalls = 0;
  for (const module of modules) {
    let tree;
    try { tree = ast(module.code); }
    catch (error) { throw new Error(`${module.file}: ${error.message}`, { cause: error }); }
    const found = [];
    for (const node of tree.body) {
      if (node.type === 'LabeledStatement') {
        const name = node.label.name;
        if (!layerName(name) || labels.has(name)) throw new Error(`Duplicate or invalid named layer: ${name}`);
        labels.add(name);
        found.push(name);
      }
      const declared = node.type === 'VariableDeclaration' ? node.declarations.flatMap((d) => bindings(d.id))
        : ['FunctionDeclaration', 'ClassDeclaration'].includes(node.type) ? bindings(node.id) : [];
      for (const name of declared) {
        if (declarations.has(name)) throw new Error(`Duplicate module declaration: ${name}`);
        declarations.add(name);
      }
      if (node.type === 'ExpressionStatement' && node.expression.type === 'CallExpression'
          && ['setcpm', 'setcps'].includes(node.expression.callee.name)) tempoCalls++;
    }
    if (module.stem !== undefined && !stemName(module.stem)) throw new Error(`Invalid stem: ${module.stem}`);
    if (found.length && !module.stem) throw new Error(`Sound layers need a stem: ${module.file}`);
    if (module.stem && !found.length) throw new Error(`Stem module has no sound layers: ${module.file}`);
    if (module.stem) (stems[module.stem] ??= []).push(...found);
  }
  if (!labels.size) throw new Error('Assembly requires named sound layers');
  if (tempoCalls !== 1) throw new Error('Assembly requires exactly one top-level setcpm/setcps call');
  // Semicolons prevent adjacent module expressions from joining through ASI.
  const code = modules.map((m, i) => `// Module ${i + 1}: ${m.file.replace(/[\r\n]/g, ' ')}\n${m.code}\n;`).join('\n\n') + '\n';
  ast(code);
  return { code, stems };
}

export async function assembleProject(manifestPath, output) {
  const manifest = resolve(manifestPath);
  const out = resolve(output);
  const raw = await readFile(manifest, 'utf8');
  const config = JSON.parse(raw);
  if (config.version !== 1 || !Array.isArray(config.modules) || !config.modules.length) throw new Error('Require version 1 and nonempty modules');
  if (typeof config.revision !== 'string' || !/^[a-z][a-z0-9_-]*$/.test(config.revision)) throw new Error('Require a lowercase revision name');
  if (!Number.isFinite(config.end_cycle) || config.end_cycle <= 0) throw new Error('Require positive end_cycle');
  const rate = config.sample_rate ?? 48000;
  if (!Number.isInteger(rate) || rate < 8000 || rate > 96000) throw new Error('Invalid sample_rate');
  for (const [name, bounds] of Object.entries(config.sections ?? {})) {
    if (!/^[a-z][a-z0-9_-]*$/.test(name) || !Array.isArray(bounds) || bounds.length !== 2
        || !bounds.every(Number.isFinite) || bounds[0] < 0 || bounds[0] >= bounds[1] || bounds[1] > config.end_cycle) throw new Error(`Invalid section: ${name}`);
  }
  const modules = [];
  for (const module of config.modules) {
    if (typeof module.file !== 'string' || !module.file) throw new Error('Every module needs a file');
    const path = resolve(dirname(manifest), module.file);
    modules.push({ ...module, path, code: await readFile(path, 'utf8') });
  }
  const { code, stems } = validateModules(modules);
  const samples = (config.samples ?? []).map((folder) => relative(out, resolve(dirname(manifest), folder)));
  await mkdir(dirname(out), { recursive: true });
  await mkdir(out);
  await mkdir(resolve(out, 'modules'));
  const records = [];
  for (const [i, module] of modules.entries()) {
    const snapshot = `modules/${String(i + 1).padStart(2, '0')}.strudel`;
    await writeFile(resolve(out, snapshot), module.code);
    records.push({ source: module.path, snapshot, sha256: hash(module.code), stem: module.stem ?? null });
  }
  await writeFile(resolve(out, 'source.strudel'), code);
  const project = { version: 1, title: config.title, revisions: { [config.revision]: { source: 'source.strudel', notes: config.notes ?? '' } },
    end_cycle: config.end_cycle, sample_rate: rate, samples, stems, sections: config.sections ?? {} };
  await writeFile(resolve(out, 'project.json'), JSON.stringify(project, null, 2) + '\n');
  await writeFile(resolve(out, 'manifest.json'), raw);
  const receipt = { status: 'complete', manifest: { source: manifest, sha256: hash(raw) }, revision: config.revision,
    modules: records, source_sha256: hash(code), project_sha256: hash(JSON.stringify(project, null, 2) + '\n'), stems };
  await writeFile(resolve(out, 'assembly.json'), JSON.stringify(receipt, null, 2) + '\n');
  return { status: 'complete', project: resolve(out, 'project.json'), source: resolve(out, 'source.strudel'), revision: config.revision, stems };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const { values, positionals } = parseArgs({ allowPositionals: true, options: { out: { type: 'string' } } });
    if (positionals.length !== 1 || !values.out) throw new Error('Usage: assemble.mjs MANIFEST --out NEW_DIRECTORY');
    console.log(JSON.stringify(await assembleProject(positionals[0], values.out), null, 2));
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
