import fs from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const rows=JSON.parse(await fs.readFile(new URL('./data.json',import.meta.url),'utf8'));
const wb=Workbook.create();
const sheets=Object.fromEntries(['Comparison','Token detail','Cost detail','Pricing','Notes'].map(n=>[n,wb.worksheets.add(n)]));
const col=n=>{let s='';for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
function table(name,title,subtitle,headers,data){
 const s=sheets[name],end=col(headers.length-1),last=5+data.length;
 s.showGridLines=false;s.getRange(`A1:${end}${last}`).format.font={name:'Arial',size:10};
 s.getRange('A1').values=[[title]];s.getRange('A1').format.font={size:18,bold:true,color:'#17354A'};
 s.getRange('A2').values=[[subtitle]];s.getRange('A2').format.font={size:10,color:'#526776'};
 s.getRange(`A5:${end}5`).values=[headers];s.getRange(`A6:${end}${last}`).values=data;
 s.tables.add(`A5:${end}${last}`,true,name.replaceAll(' ','')+'Table');
 s.getRange(`A5:${end}5`).format={fill:'#17354A',font:{bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:44};
 s.getRange(`A6:${end}${last}`).format.rowHeight=24;
 s.getRange(`A1:${end}${last}`).format.columnWidth=17;s.getRange(`A1:A${last}`).format.columnWidth=29;
 s.getRange(`A1:${end}1`).format.rowHeight=30;
 s.freezePanes.freezeRows(5);s.freezePanes.freezeColumns(1);
 return s;
}
const sorted=[...rows].sort((a,b)=>(a[16]??Infinity)-(b[16]??Infinity)||b[1]-a[1]);
const tok=table('Token detail','Output-token use','Source values • weighted per-task averages and unweighted evaluation totals • blanks = unavailable',
 ['Model / effort','Intelligence','Score status','Omniscience accuracy','Output tokens / task','Answer tokens / task','Reasoning tokens / task','Total output tokens','Total answer tokens','Total reasoning tokens'],
 sorted.map(r=>[r[0],r[1],r[2],r[3],...r.slice(7,10),...r.slice(4,7)].map(v=>v??null)));
tok.getRange('D6:D25').setNumberFormat('0.00%');tok.getRange('E6:G25').setNumberFormat('#,##0.0');tok.getRange('H6:J25').setNumberFormat('#,##0');
const cost=table('Cost detail','Benchmark cost breakdown · USD','Source totals are rounded independently; component sums may differ. Per-task costs are weighted.',
 ['Model / effort','Total cost / task','Answer / task','Reasoning / task','Cache write / task','Cache hit / task','Input / task','Total run cost','Total answer cost','Total reasoning cost','Total cache write','Total cache read','Total input cost'],
 sorted.map(r=>[r[0],...Array.from({length:6},(_,i)=>r[16+i]??null),...Array.from({length:6},(_,i)=>r[10+i]??null)]));
cost.getRange('B6:F25').setNumberFormat('$0.00');cost.getRange('G6:G25').setNumberFormat('$0.0000');cost.getRange('H6:M25').setNumberFormat('$#,##0');
const comp=table('Comparison','GPT model efficiency · Artificial Analysis','Captured 8 Sep 2026 • sorted by cost/task ascending; missing results last • ratios are proxies, not task success',
 ['Model / effort','Intelligence','Score status','Accuracy','USD / task','Output tokens / task','Points / $','Cost-efficiency rank','Points / 1k tokens','Token-efficiency rank','Reasoning share'],
 sorted.map(r=>[r[0],null,r[2],null,null,null,null,null,null,null,null]));
for(let i=6;i<=25;i++){
 for(const [c,f] of Object.entries({B:`='Token detail'!B${i}`,D:`='Token detail'!D${i}`,E:`=IF(C${i}="Estimated","",'Cost detail'!B${i})`,F:`=IF(C${i}="Estimated","",'Token detail'!E${i})`,G:`=IF(C${i}="Estimated","",B${i}/E${i})`,H:`=IF(C${i}="Estimated","",1+COUNTIF($G$6:$G$25,">"&G${i}))`,I:`=IF(C${i}="Estimated","",B${i}/F${i}*1000)`,J:`=IF(C${i}="Estimated","",1+COUNTIF($I$6:$I$25,">"&I${i}))`,K:`=IF(C${i}="Estimated","",'Token detail'!G${i}/F${i})`}))comp.getRange(`${c}${i}`).formulas=[[f]];
}
comp.getRange('D6:D25').setNumberFormat('0.00%');comp.getRange('E6:E25').setNumberFormat('$0.00');comp.getRange('F6:F25').setNumberFormat('#,##0.0');comp.getRange('G6:G25').setNumberFormat('0.00');comp.getRange('I6:I25').setNumberFormat('0.00');comp.getRange('K6:K25').setNumberFormat('0.0%');
comp.getRange('B6:K25').format.font.color='#17354A';
const pricing=table('Pricing','API token prices · USD per million tokens','Prices from the AA pricing chart • same listed rates across selected effort levels • not Codex allowance rates',
 ['Model family','Input / 1M','Cached input / 1M','Output / 1M'],
 [['GPT-5.6 Luna',0.2,0.02,1.2],['GPT-5.6 Terra',2,0.2,12],['GPT-5.6 Sol',4,0.4,20],['GPT-6 Astra',10,1,50]]);
pricing.getRange('B6:D9').setNumberFormat('$0.00');
const slugs=['gpt-6-astra','gpt-5-6-sol','gpt-5-6-terra','gpt-5-6-luna'].flatMap(r=>['','-xhigh','-high','-medium','-low'].map(e=>r+e));
const base='https://artificialanalysis.ai/models?models='+slugs.join('%2C');
const notes=[
 ['Scope','20 selected model/effort configurations; 15 have token/cost results. Five Intelligence Index scores are marked estimates by AA.'],
 ['Capture','2026-09-08. Values transcribed from publicly visible chart labels and keyboard-accessible tooltips.'],
 ['Sorting','Comparison, Token detail and Cost detail share cost/task ascending order, with missing results last. Excel table filters allow alternate sorting.'],
 ['Intelligence','Artificial Analysis Intelligence Index v4.3, displayed whole-number scores. “Evaluated” means not marked as estimated in the chart.'],
 ['Efficiency formulas','Points / $ = Intelligence Index / weighted USD per task. Points / 1k tokens = Intelligence Index × 1,000 / weighted output tokens per task. Higher is better.'],
 ['Interpretation','These ratios are descriptive benchmark proxies. Index points are not cardinal units of useful work; they do not measure coding success, reliability or cost per successful task.'],
 ['Rank rules','Ranks are descending ratio, with ties sharing rank. Estimated scores / missing token or cost results are excluded. Ranks recalculate; physical row order does not.'],
 ['Token definition','Output tokens include answer and reasoning tokens, not input tokens. Selected charts do not provide total input-token counts.'],
 ['Weighting','Per-task values are weighted across Intelligence Index evaluations. Run totals are not weighted per-task averages; do not divide totals to reconstruct weighted averages.'],
 ['Cost definition','Benchmark cost includes answer, reasoning, cache write, cache read/hit and noncached input. Pricing sheet shows listed per-million-token rates.'],
 ['Precision','Token totals are integer tooltip values; per-task tokens have one decimal; accuracy has two percentage decimals. Cost totals are whole USD; most per-task cost values have two decimals. Small input costs retain four decimals.'],
 ['Rounding','Components and totals are rounded independently. Preserve the reported totals instead of forcing sums to match. Calculated ratios inherit this precision limitation.'],
 ['Missing results','Luna High, Medium and Low; Terra Medium and Low: estimated intelligence scores, with no cost/token data in the selected charts. Blanks mean unavailable, not zero.'],
 ['Accuracy','AA-Omniscience accuracy is the fraction of all questions answered correctly, irrespective of whether the model attempts an answer. It is separate from the multi-benchmark Intelligence Index.'],
 ['No mixed denominators','Do not divide Intelligence Index task costs by Omniscience accuracy to infer cost per correct answer: they refer to different evaluation scopes.'],
 ['Naming','Unsuffixed model URLs map to max in these charts. Source “GPT-6 Astra (low)” corresponds to the skill’s Astra Light label. Source labels are retained.'],
 ['Codex caveat','API dollars and raw token counts do not establish Codex subscription allowance consumption. Parent re-entry, caching, context size and retries require separate rollout telemetry.'],
 ['Routing caveat','Benchmark comparisons alone do not justify changing the Agent Deployment policy. Test bounded tasks, review outcomes and total orchestration cost before making routing changes.'],
 ['Intelligence source',base+'#artificial-analysis-intelligence-index'],
 ['Token-use source',base+'&intelligence-index-token-use=intelligence-vs-output-tokens-per-task#intelligence-index-token-use-tabs'],
 ['Total-cost source',base+'#total-cost-tabs'],
 ['Per-task-cost source',base+'#cost-tabs'],
 ['Accuracy source',base+'&omniscience=omniscience-accuracy#omniscience-tabs'],
 ['Pricing source',base+'#pricing-tabs']
];
const n=table('Notes','Sources & methodology','Read before interpreting efficiency rankings',['Topic','Definition / source'],notes);
n.getRange('B1:B29').format.columnWidth=115;n.getRange('B6:B29').format.wrapText=true;n.getRange('A6:B29').format.rowHeight=48;n.getRange('A24:B29').format.rowHeight=85;
await wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Comparison!A5:K10',include:'values',tableMaxRows:6,tableMaxCols:11,maxChars:6000})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},maxChars:2000})).ndjson);
for(const [name,range] of [['Comparison','A1:K13'],['Token detail','A1:J11'],['Cost detail','A1:M11'],['Pricing','A1:D10'],['Notes','A1:B14']]){
 const img=await wb.render({sheetName:name,range,scale:1,format:'png'});
 await fs.writeFile(new URL('./'+name.replaceAll(' ','-')+'.png',import.meta.url),new Uint8Array(await img.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(fileURLToPath(new URL('./GPT-model-efficiency-2026-09-08.xlsx',import.meta.url)));
console.log('Export complete');
