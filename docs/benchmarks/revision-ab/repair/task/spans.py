"""Coalesce byte spans for batch retrieval."""


def compact_ranges(ranges):
    ranges.sort()
    merged = []
    for start, end in ranges:
        if merged and start < merged[-1][1]:
            merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))
    return merged
