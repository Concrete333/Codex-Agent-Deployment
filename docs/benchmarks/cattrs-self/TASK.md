# Upgrade recursive type resolution

This is a pinned cattrs 24.1.3 checkout. Add support for `typing.Self` (including
`typing_extensions.Self` on this Python) to the generated Converter's recursive
structure/unstructure paths. Preserve existing public signatures and behavior
for types that do not use Self. Do not upgrade or replace the library wholesale.

## Required contract

- In an attrs class or dataclass, `Optional[Self]` denotes the actual target
  class being converted. Nested objects must structure and unstructure correctly.
  Fields with a None default and inherited Self fields must work; when converting
  a subclass, nested values must become that subclass, not its parent.
- Support the same recursive optional field in TypedDicts, alongside ordinary
  typed fields. Honor registered primitive hooks at every recursion depth.
- Support recursive optional fields in NamedTuples when the existing
  `namedtuple_dict_structure_factory` and `namedtuple_dict_unstructure_factory`
  are registered. Dictionary representation is required for this path.
- Different Self-bearing classes can occur in one object graph. Never register
  a converter-wide Self hook bound to one class: resolution is local to the
  containing target. Separate Converter instances must retain their own hooks.
- Both detailed_validation=True and False must work. None terminates recursion;
  preserve existing validation behavior for ordinary fields.
- Existing converters, generated hooks, collections, generics, factory hooks
  and non-Self recursive behavior must keep working. Add focused regression tests
  for the new behavior and run the relevant existing tests.

Example: a dataclass Node with fields `value: int` and `child: Optional[Self]`
must structure `{'value': '1', 'child': {'value': '2', 'child': None}}` into
Node(1, Node(2, None)), and unstructure it back to integer-valued dictionaries.

The attrs/dataclass generators, TypedDict generators and NamedTuple factories
are separate paths in this repository. Discover their consumers and shared
helpers before changing them; keep shared decisions consistent. How to split
the work is up to you. Do not force delegation or duplicate an active worker's
investigation.

## Scope and checks

Python 3.12 and prepared dependencies are provided; use the supplied Python
executable. Set PYTHONPATH to this checkout's `src` when running tests. A useful
existing-test command is:

`python -B -m pytest -o addopts= -p no:cacheprovider -q tests/test_baseconverter.py tests/test_converter.py tests/test_cols.py tests/test_copy.py tests/test_dataclasses.py tests/test_factory_hooks.py tests/test_gen.py tests/test_gen_dict.py tests/test_generics.py tests/test_optionals.py tests/test_recursive.py tests/test_typeddicts.py --hypothesis-seed=1701`

Use FAST=1 for the repository's bounded Hypothesis profile. Do not change existing
tests or weaken assertions; add tests in new files. No network, new dependencies,
other checkouts, benchmark graders, later upstream code or shell-launched model
processes. Only this checkout may be edited. Finish with changes, checks and
unresolved issues. Supporting BaseConverter, cyclic runtime objects, new public
APIs, or unrelated library upgrades is not required.
