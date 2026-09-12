# Implement normalize_labels

Implement `normalize_labels(values)` in labels.py. Change only that file.

The input must be a list, and each element must be a string; otherwise raise TypeError. Strip surrounding whitespace and apply str.casefold() to each value. Discard empty normalized strings, remove duplicates, and preserve first-occurrence order. Return a new list without modifying the input. Empty input returns an empty list. Preserve punctuation and internal whitespace.

Use only the standard library. The host runs check_labels.py for final verification; you may run it during development if needed. Do not modify TASK.md, check_labels.py or bridge files. Do not start background processes or delegates. Report unresolved issues explicitly.
