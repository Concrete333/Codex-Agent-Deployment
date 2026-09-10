# Revision A/B component fixture

This directory is fixture preparation, not a measured run. Copy only `task/`
into a trial checkout. Keep `grade.py`, `reference.py`, `mutants.py`, and
`protected_hashes.json` outside the participant-visible checkout.

Preflight from this directory:

```powershell
python -m unittest discover -s task -q
python grade.py --reference
python grade.py task
python grade.py --mutant alias
python grade.py --mutant sliding
```

The public suite and reference must pass. The unimplemented baseline and both
deliberately flawed mutations must fail the external feature checks.
