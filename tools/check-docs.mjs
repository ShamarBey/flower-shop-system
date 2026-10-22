import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse } from 'yaml';
import { Parser } from '@dbml/core';

const root = new URL('../', import.meta.url);
const read = path => readFileSync(new URL(path, root), 'utf8');
const api = parse(read('openapi.yaml'));
const architecture = read('ARCHITECTURE.md');
assert.ok(architecture.includes(read('docs/diagrams/c4-container.mmd').trim()), 'Mermaid C4 должен совпадать с ARCHITECTURE');
const methods = ['get', 'post', 'put', 'patch', 'delete'];
const actual = Object.entries(api.paths).flatMap(([path, operations]) => methods.filter(m => operations[m]).map(m => `${m.toUpperCase()} ${path}`)).sort();
const documented = [...architecture.matchAll(/^\| (GET|POST|PUT|PATCH|DELETE) \| `([^`]+)`/gm)].map(m => `${m[1]} ${m[2]}`).sort();
assert.deepEqual(documented, actual, 'Таблица ARCHITECTURE должна совпадать с OpenAPI');
for (const path of ['/health', '/products', '/products/{productId}']) {
  assert.deepEqual(api.paths[path].get.security, [], `${path} должен быть публичным`);
}
const ids = Object.values(api.paths).flatMap(path => methods.filter(m => path[m]).map(m => path[m].operationId));
assert.equal(new Set(ids).size, ids.length, 'operationId должны быть уникальны');

const schema = Parser.parse(read('docs/diagrams/erd.dbml'), 'dbmlv2').export().schemas[0];
const svg = read('docs/diagrams/erd.svg');
const xmlDecode = value => value.replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n))).replaceAll('&gt;', '>').replaceAll('&lt;', '<').replaceAll('&amp;', '&');
const nodes = [...svg.matchAll(/class="node">\s*<title>([^<]+)<\/title>/g)].map(m => xmlDecode(m[1])).sort();
assert.deepEqual(nodes, schema.tables.map(t => t.name).sort(), 'SVG должен содержать все таблицы DBML');
const edges = [...svg.matchAll(/class="edge">\s*<title>([^<]+)<\/title>/g)].map(m => xmlDecode(m[1])).sort();
const expectedEdges = schema.refs.map(ref => ref.endpoints.map((e, i) => `${e.tableName}:${i ? 'w' : 'e'}`).join('->')).sort();
assert.deepEqual(edges, expectedEdges, 'Все связи SVG должны точно соответствовать DBML');
const tooltips = [...svg.matchAll(/xlink:title="([^"]+)"/g)].map(m => xmlDecode(m[1])).sort();
const expectedTooltips = schema.refs.map(ref => ref.endpoints.map(e => `${e.tableName}.${e.fieldNames[0]}`).join(' -> ')).sort();
assert.deepEqual(tooltips, expectedTooltips, 'FK-поля каждой связи SVG должны соответствовать DBML');
for (const table of schema.tables) {
  assert.ok(table.fields.some(f => f.pk) || table.indexes.some(i => i.pk), `${table.name}: отсутствует PK`);
}
for (const [name, forbidden] of [['orders', ['subtotal', 'total']], ['order_items', ['line_total']]]) {
  const table = schema.tables.find(t => t.name === name);
  assert.ok(table.fields.every(f => !forbidden.includes(f.name)), `${name}: расчетные суммы должны оставаться в API, а не в ERD`);
}
// Каждый FK должен быть первым столбцом хотя бы одного индекса или PK.
for (const ref of schema.refs) {
  const child = ref.endpoints[1];
  const table = schema.tables.find(t => t.name === child.tableName);
  const indexed = new Set([
    table.fields.filter(f => f.pk)[0]?.name,
    ...table.fields.filter(f => f.unique).map(f => f.name),
    ...table.indexes.map(i => i.columns[0]?.value),
  ]);
  assert.ok(indexed.has(child.fieldNames[0]), `${child.tableName}.${child.fieldNames[0]}: нет индекса FK`);
}

const markdown = ['README.md', 'ARCHITECTURE.md', 'docs/use-cases.md', 'docs/domain-model.md', 'docs/business-rules.md', 'docs/control-questions.md', 'docs/control-questions-lab2.md', 'docs/control-questions-lab3.md', 'docs/control-questions-lab4.md', 'docs/lab3.md', 'docs/lab4.md', 'docs/validation-report.md', 'docs/defense-checklist.md', 'docs/defense-guide.md'];
for (const path of markdown) {
  for (const match of read(path).matchAll(/\[[^\]]*\]\(([^)]+)\)/g)) {
    if (/^(https?:|#)/.test(match[1])) continue;
    assert.ok(existsSync(resolve(fileURLToPath(root), dirname(path), match[1].split('#')[0])), `${path}: неверная ссылка ${match[1]}`);
  }
}
console.log(`OK: ${actual.length} операций API, ${schema.tables.length} таблиц, ${edges.length} связей; доступ к каталогу, индексы FK и ссылки согласованы.`);
