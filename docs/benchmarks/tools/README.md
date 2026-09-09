# Benchmark maintenance tools

These scripts are maintenance utilities, not operational skill context.

- `combine-model-evidence.py` requires Python 3.10+ and `openpyxl`. It reads the raw GPT capture, corrected GPT workbook and copied Claude-only workbook, checks their reconciliation, and generates `docs/model-performance-comparison.md`. Pass `--check` to check reproducibility without writing. It does not alter the workbooks.

The JavaScript utilities require Node.js and `@oai/artifact-tool`:

- `review-cost-policy.mjs` reads the canonical GPT workbook and raw metrics in the parent directory. Pass `--checks` to compare workbook values with the raw data. It does not modify either file.
- `initial-workbook/build.mjs` and its `data.json` preserve the initial workbook-generation inputs. They predate the corrected decimal scores and added configurations; do not use their output to replace the canonical workbook. Running the script writes a draft workbook and preview images beside the script.

The corrected GPT workbook, Claude-only workbook and raw GPT metrics remain the source data. The older mixed `agent-model-selection-2026-09-08.xlsx` is historical: its Task Fit conditional non-hallucination ranking is not a valid cross-vendor wrong-answer ranking. Use the combined Markdown comparison and its interpretation notes instead. Generated previews and inspection dumps are not retained here.
