import { parse } from 'acorn';

export function selectLayers(code, solo = []) {
  const ast = parse(code, { ecmaVersion: 'latest', allowAwaitOutsideFunction: true });
  const labels = ast.body.filter((node) => node.type === 'LabeledStatement').map((node) => node.label);
  const names = labels.map((label) => label.name);
  if (solo.length) {
    if (new Set(names).size !== names.length || names.some((name) => !/^[a-z][A-Za-z0-9_]*$/.test(name) || name.endsWith('_'))) {
      throw new Error('Stem export requires unique lowercase-leading named labels, e.g. drums: and bass:');
    }
    for (const name of solo) if (!names.includes(name)) throw new Error(`Unknown layer: ${name}`);
    // Use Strudel's native mute-label syntax. AST offsets keep strings/comments
    // and multiline expressions untouched; originals are never rewritten on disk.
    for (const label of labels.toReversed()) {
      if (!solo.includes(label.name)) code = code.slice(0, label.start) + '_' + code.slice(label.start);
    }
  }
  return { code, labels: names };
}
