import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { Parser } from '@dbml/core';
import { instance } from '@viz-js/viz';

const folder = new URL('../docs/diagrams/', import.meta.url);
const schema = Parser.parse(readFileSync(new URL('erd.dbml', folder), 'utf8'), 'dbmlv2').export().schemas[0];
const html = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const fk = new Set(schema.refs.flatMap(ref => ref.endpoints.slice(1).flatMap(e => e.fieldNames.map(f => `${e.tableName}.${f}`))));
const lines = [
  'digraph ERD {',
  'graph [rankdir=LR, bgcolor="white", pad="0.4", nodesep="0.6", ranksep="1.3", splines=polyline, fontname="Arial", label="Цветочный магазин — ERD из erd.dbml\\nPK — первичный ключ; FK — внешний ключ; UQ — уникальность; NN — NOT NULL\\n1 / 0..1 / 0..* — кратность на соответствующем конце связи", labelloc=t, fontsize=20];',
  'node [shape=plain, fontname="Arial"];',
  'edge [color="#64748b", fontname="Arial", fontsize=10, dir=none, labeldistance=2.5];',
];
for (const table of schema.tables) {
  const primary = new Set([...table.fields.filter(f => f.pk).map(f => f.name), ...table.indexes.filter(i => i.pk).flatMap(i => i.columns.map(c => c.value))]);
  const rows = table.fields.map(field => {
    const marks = [primary.has(field.name) && 'PK', fk.has(`${table.name}.${field.name}`) && 'FK', field.unique && 'UQ', (field.not_null || primary.has(field.name)) && 'NN'].filter(Boolean).join(' ');
    return `<TR><TD PORT="${field.name}" ALIGN="LEFT">${html(field.name)}</TD><TD ALIGN="LEFT">${html(field.type.type_name)}</TD><TD PORT="out_${field.name}" ALIGN="LEFT">${marks}</TD></TR>`;
  });
  lines.push(`"${table.name}" [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="7"><TR><TD COLSPAN="3" BGCOLOR="#dbeafe"><B>${table.name}</B></TD></TR>${rows.join('')}</TABLE>>];`);
}
for (const ref of schema.refs) {
  const [parent, child] = ref.endpoints;
  const childTable = schema.tables.find(t => t.name === child.tableName);
  const primary = new Set(childTable.indexes.filter(i => i.pk).flatMap(i => i.columns.map(c => c.value)));
  const required = child.fieldNames.every(name => {
    const f = childTable.fields.find(f => f.name === name);
    return f.pk || f.not_null || primary.has(name);
  });
  lines.push(`"${parent.tableName}":"out_${parent.fieldNames[0]}":e -> "${child.tableName}":"${child.fieldNames[0]}":w [tooltip="${parent.tableName}.${parent.fieldNames[0]} -> ${child.tableName}.${child.fieldNames[0]}", taillabel="${required ? '1' : '0..1'}", headlabel="${child.relation === '*' ? '0..*' : '0..1'}"];`);
}
lines.push('}');
const dot = lines.join('\n') + '\n';
writeFileSync(new URL('erd.dot', folder), dot);
const viz = await instance();
const svg = viz.renderString(dot, { format: 'svg', engine: 'dot' }).replace(/<!DOCTYPE[\s\S]*?>\s*/, '');
writeFileSync(new URL('erd.svg', folder), svg);
const c4 = viz.renderString(readFileSync(new URL('c4-container.dot', folder), 'utf8'), { format: 'svg', engine: 'dot' }).replace(/<!DOCTYPE[\s\S]*?>\s*/, '');
writeFileSync(new URL('c4-container.svg', folder), c4);
console.log(`ERD: ${schema.tables.length} таблиц, ${schema.refs.length} связей. SVG: ${fileURLToPath(new URL('erd.svg', folder))}`);
