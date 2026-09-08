import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
import { fileURLToPath } from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(root+'GPT-model-efficiency-2026-09-08.xlsx'));
const raw=JSON.parse(await fs.readFile(root+'openai-metrics-raw-2026-09-08.json','utf8'));
if (!process.argv.includes('--checks')) {
const cols=['short_name','intelligence_index','cost_per_task_usd','output_tokens_per_task','time_per_task_min','eval_Terminal_Bench_v4_0','eval_SciCode','eval_AutomationBench_AA','eval_AA_LCR_v1_1'];
console.log(cols.join(' | '));
for(const r of raw.rows.filter(r=>/^GPT-(5\.6|6)/.test(r.short_name)))console.log(cols.map(c=>typeof r[c]==='number'?Math.round(r[c]*10000)/10000:r[c]??null).join(' | '));
const eligible=raw.rows.filter(r=>Number.isFinite(r.intelligence_index)&&r.cost_per_task_usd>0);
console.log('FRONTIER',eligible.filter(r=>!eligible.some(o=>o!==r&&o.intelligence_index>=r.intelligence_index&&o.cost_per_task_usd<=r.cost_per_task_usd&&(o.intelligence_index>r.intelligence_index||o.cost_per_task_usd<r.cost_per_task_usd))).map(r=>r.short_name));
}
if (process.argv.includes('--checks')) {
 const comp=wb.worksheets.getItem('Comparison');
 console.log('HEADERS',JSON.stringify(comp.getRange('A5:N5').values));
 console.log('COMPARISON',JSON.stringify(comp.getRange('A6:N27').values));
 console.log('FORMULAS',JSON.stringify(comp.getRange('L6:N6').formulas));
 console.log('NOTES',JSON.stringify(wb.worksheets.getItem('Notes').getRange('A6:B33').values));
 const mismatches=[];
 for(const r of comp.getRange('A6:N27').values){
  const src=raw.rows.find(x=>x.short_name===r[0]);
  if(!src){mismatches.push([r[0],'missing raw record']);continue;}
  if(Math.abs(r[1]-src.intelligence_index)>0.051)mismatches.push([r[0],'score mismatch']);
  if(typeof r[4]==='number'&&r[4]!==src.cost_per_task_usd)mismatches.push([r[0],'cost mismatch']);
 }
 console.log('WORKBOOK_RAW_MISMATCHES',JSON.stringify(mismatches));
}
