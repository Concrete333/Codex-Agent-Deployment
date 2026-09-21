// Maintenance only. Run with the bundled @oai/artifact-tool dependency.
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
import { Workbook, SpreadsheetFile } from "@oai/artifact-tool";

const root = process.argv[2];
assert(root, "Pass the agent-deployment repository root.");
const bench = path.join(root, "docs/benchmarks");
const data = JSON.parse((await fs.readFile(path.join(bench, "mimo-comparison-2026-09-21.json"), "utf8")).replace(/^\uFEFF/, ""));
const names = ["MiMo-V2.6-Pro", "Luna Max", "Sol High", "Opus 5 Low", "Astra High"];
const models = [];
for (let i = 0; i < data.pages.length; i++) {
  const page = data.pages[i];
  assert.equal(page.benchmark, "Intelligence Index v4.3.2");
  for (const col of i === 0 ? [1, 2] : [2]) {
    models.push({ name: col === 1 ? names[0] : names[i + 1],
      source: page.url, label: page.table[0][col],
      raw: Object.fromEntries(page.table.filter(r => r.length >= 3 && r[0]).map(r => [r[0], r[col]])) });
  }
}
function numeric(text) {
  if (!text || /^(N\/A|—)$/.test(text)) return null;
  const match = text.replaceAll("−", "-").replaceAll(",", "").match(/^\$?(-?[\d.]+)([kM%])?(?:s)?(?:\s|$)/);
  assert(match, "Unexpected numeric source: " + text);
  const scale = { k: 1000, M: 1000000, "%": 0.01 };
  return Number(match[1]) * (scale[match[2]] ?? 1);
}
const value = (model, metric) => numeric(model.raw[metric]);
models.sort((a, b) => value(a, "Cost per Task") - value(b, "Cost per Task"));
assert.equal(models.length, 5);
assert.equal(value(models[0], "Intelligence Index"), 46);
assert.equal(value(models[0], "Cost per Task"), 0.13);
assert(Math.abs(value(models[0], "Terminal-Bench 4.0") - 0.35) < 1e-12);
assert.equal(data.kilo.cli_model, "kilo/xiaomi/mimo-v2.6-pro");
assert.equal(data.kilo.variants.thinking.reasoning.enabled, true);

const wb = Workbook.create();
const comparison = wb.worksheets.add("Comparison");
const metrics = wb.worksheets.add("Metrics");
function base(sheet) {
  sheet.showGridLines = false;
  sheet.getRange("A1:H40").format.font = { name: "Arial", size: 10, color: "#202B36" };
  sheet.getRange("A1:H40").format.rowHeight = 22;
}
function title(sheet, text) {
  sheet.getRange("A2").values = [[text]];
  sheet.getRange("A2").format.font = { name: "Arial", size: 14, bold: true, color: "#202B36" };
}
function header(sheet, range) {
  sheet.getRange(range).format = { fill: "#253C56", font: { bold: true, color: "#FFFFFF" },
    wrapText: true, rowHeight: 36, verticalAlignment: "center" };
}
base(comparison); base(metrics);
title(comparison, "MiMo and delegation candidates");
comparison.getRange("A3").values = [["21 September 2026 | Intelligence Index v4.3.2 | sorted by benchmark task cost, lowest first"]];
comparison.getRange("A5:G5").values = [["Model", "Intelligence index", "Cost / task ($)", "Terminal-Bench 4.0", "Omniscience index", "Output tokens / task (approx.)", "Reasoning tokens / task (approx.)"]];
header(comparison, "A5:G5");
comparison.getRange("A6:G10").values = models.map(m => [m.name, value(m, "Intelligence Index"),
  value(m, "Cost per Task"), value(m, "Terminal-Bench 4.0"), value(m, "AA-Omniscience"),
  value(m, "Output Tokens per Task"), value(m, "Reasoning Tokens per Task")]);
comparison.getRange("A5:A10").format.columnWidth = 22;
comparison.getRange("B5:G10").format.columnWidth = 18;
comparison.getRange("C6:C10").setNumberFormat("$0.00");
comparison.getRange("D6:D10").setNumberFormat("0%");
comparison.getRange("F6:G10").setNumberFormat("#,##0");
comparison.getRange("A13").values = [["Costs are API-priced benchmark averages, not Codex allowance or accepted repository-task costs."]];
comparison.getRange("A14").values = [["Public-table precision only. No graph data downloaded. Do not mix with the archived v4.3 capture."]];
comparison.getRange("A15").values = [["MiMo beats Luna Max, Sol High and Opus 5 Low on coding and task cost; their full results differ by task."]];
comparison.getRange("A16").values = [["Omniscience is a knowledge metric, not a hallucination percentage or reviewer qualification."]];
comparison.getRange("A18").values = [["Kilo default: kilo/xiaomi/mimo-v2.6-pro / thinking. Catalog checked; no paid MiMo implementation trial yet."]];

title(metrics, "Published metrics");
metrics.getRange("A3").values = [["Same capture and model order as Comparison. Missing values remain blank; source labels retained below."]];
metrics.getRange("A5:G5").values = [["Metric", "Unit", ...models.map(m => m.name)]];
header(metrics, "A5:G5");
const fields = [
  ["Intelligence Index", "points"], ["AA-Briefcase v1.1", "Elo"], ["GDPval-AA v2.1", "Elo"],
  ["AutomationBench-AA", "fraction"], ["Terminal-Bench 4.0", "fraction"], ["SciCode", "fraction"],
  ["Humanity's Last Exam", "fraction"], ["GDP.pdf", "fraction"], ["CritPt", "fraction"],
  ["AA-Omniscience", "points"], ["AA-LCR v1.1", "fraction"],
  ["Cost per Task", "USD/task"], ["Input Price per 1M Tokens", "USD/1M tokens"],
  ["Output Price per 1M Tokens", "USD/1M tokens"], ["Cache Hit Price per 1M Tokens", "USD/1M tokens"],
  ["Cost to Run Intelligence Index", "USD (rounded)"],
  ["Output Tokens per Task", "tokens (approx.)"], ["Reasoning Tokens per Task", "tokens (approx.)"],
  ["Output Tokens to Run Intelligence Index", "tokens (approx.)"],
  ["Output Speed", "tokens/s"], ["Time to First Token", "seconds"], ["Time to First Answer Token", "seconds"],
  ["Time per Task", "seconds"],
];
metrics.getRange(`A6:G${5 + fields.length}`).values = fields.map(([key, unit]) => [key, unit, ...models.map(m => value(m, key))]);
metrics.getRange("A5:A30").format.columnWidth = 40;
metrics.getRange("B5:B30").format.columnWidth = 21;
metrics.getRange("C5:G30").format.columnWidth = 22;
for (let i = 0; i < fields.length; i++) {
  const unit = fields[i][1];
  metrics.getRange(`C${i + 6}:G${i + 6}`).setNumberFormat(
    unit === "fraction" ? "0%" : unit === "USD/task" ? "$0.00" :
    unit === "USD/1M tokens" ? "$0.0000" : unit === "USD (rounded)" ? "$#,##0" :
    unit === "seconds" ? "0.00" : "#,##0");
}
metrics.getRange("A30:G30").values = [["Source configuration", "", ...models.map(m => m.label)]];
metrics.getRange("A30:G30").format.wrapText = true;
metrics.getRange("A30:G30").format.rowHeight = 58;
const sources = [...new Set(models.map(m => m.source))];
for (let i = 0; i < sources.length; i++) {
  metrics.getRange(`A${32 + i}`).values = [[sources[i]]];
}
metrics.getRange("A38").values = [["Kilo catalog: input $0.435/M, output $0.87/M, cache read $0.0036/M; thinking enables reasoning."]];
metrics.getRange("A39").values = [["Exact displayed strings, source URLs and catalog variants are retained in mimo-comparison-2026-09-21.json."]];
metrics.freezePanes.freezeRows(5);
wb.recalculate();
assert.deepEqual(comparison.getRange("C6:C10").values.flat(), [0.13, 0.18, 0.81, 1.10, 1.73]);
const inspection = await wb.inspect({kind: "table", range: "Comparison!A5:G10", include: "values",
  tableMaxRows: 6, tableMaxCols: 7, maxChars: 1800});
console.log(inspection.ndjson);
for (const [sheetName, range] of [["Comparison", "A1:G19"], ["Metrics", "A1:G39"]]) {
  const preview = await wb.render({sheetName, range, scale: 1.5, format: "png"});
  await fs.writeFile(path.join(path.dirname(process.argv[1]), sheetName + ".png"), new Uint8Array(await preview.arrayBuffer()));
}
const output = await SpreadsheetFile.exportXlsx(wb);
await output.save(path.join(bench, "mimo-model-comparison-2026-09-21.xlsx"));
const rows = models.map(m => `| ${m.name} | ${m.raw["Intelligence Index"]} | ${m.raw["Cost per Task"]} | ${m.raw["Terminal-Bench 4.0"]} | ${m.raw["AA-Omniscience"]} | ${m.raw["Output Tokens per Task"]} |`);
const md = [
  "# MiMo-V2.6-Pro comparison",
  "Maintenance evidence only; not loaded during ordinary skill use.",
  "Captured 21 September 2026 from Artificial Analysis's visible comparison tables, Intelligence Index v4.3.2. No graph dataset was downloaded. Rounded display values are retained; do not merge these into the archived 8 September v4.3 rankings.",
  "## Current comparison",
  "Sorted by API-priced benchmark cost per task, lowest first. These are not subscription usage or prices for accepted repository work.",
  "| Configuration | Index | $/task | Terminal-Bench 4.0 | Omniscience index | Output tokens/task (approx.) |",
  "| --- | ---: | ---: | ---: | ---: | ---: |",
  ...rows,
  "",
  "## Implications",
  "MiMo is a promising bounded implementation candidate: this capture shows a higher coding score and lower benchmark task cost than Luna Max, Sol High and Opus 5 Low. It also emits more output tokens. These measures do not establish real-task savings or justify broadening Kilo's task scope.",
  "Its Omniscience Index is below Sol, Opus and Astra in this comparison. This is a knowledge-reliability index, not a hallucination rate or a measured ability to review code. Keep consequential decisions and acceptance with Codex.",
  "## Runtime",
  "The installed Kilo catalog lists `kilo/xiaomi/mimo-v2.6-pro` as active, with `thinking` (reasoning enabled) and `instant` (reasoning disabled) variants. The default is `thinking`; it matches the reasoning model label, not a proven identical benchmark harness. Kilo catalog rates are $0.435 input, $0.87 output and $0.0036 cached input per million tokens. Kilo 7.7.6 resolved the requested model, variant and step limit for implement, explore and review profiles; the latter two also passed the existing permission checks, without inference. Catalog availability and offline configuration tests do not replace a paid implementation test.",
  "## Evidence",
  "- [Workbook](benchmarks/mimo-model-comparison-2026-09-21.xlsx): comparison and full captured numerical metrics.",
  "- [Visible table capture and Kilo metadata](benchmarks/mimo-comparison-2026-09-21.json): exact displayed strings and capture time.",
  "- [Model page](https://artificialanalysis.ai/models/mimo-v2-6-pro).",
  ...data.pages.map(p => `- [${p.table[0][2]} comparison](${p.url}).`),
  "",
].join("\n\n").replaceAll("|\n\n|", "|\n|");
await fs.writeFile(path.join(root, "docs/mimo-model-selection-2026-09-21.md"), md);
console.log("Saved workbook and evidence note.");
