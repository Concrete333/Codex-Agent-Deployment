# Benchmark maintenance tools

These scripts are maintenance utilities, not operational skill context. They require Node.js and `@oai/artifact-tool`.

- `review-cost-policy.mjs` reads the canonical GPT workbook and raw metrics in the parent directory. Pass `--checks` to compare workbook values with the raw data. It does not modify either file.
- `initial-workbook/build.mjs` and its `data.json` preserve the initial workbook-generation inputs. They predate the corrected decimal scores and added configurations; do not use their output to replace the canonical workbook. Running the script writes a draft workbook and preview images beside the script.

The corrected workbooks and raw metrics in `docs/benchmarks/` remain the reference data. Generated previews, inspection dumps, and superseded skill drafts are not retained here.
