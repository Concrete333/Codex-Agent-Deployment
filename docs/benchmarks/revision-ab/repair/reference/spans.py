"""Reference using an endpoint sweep, independent of a running-end merge."""


def compact_ranges(ranges):
    events = {}
    for pair in ranges:
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise ValueError('pair required')
        lo, hi = pair
        if type(lo) is not int or type(hi) is not int or lo > hi:
            raise ValueError('invalid endpoints')
        if lo == hi:
            continue
        events[lo] = events.get(lo, 0) + 1
        events[hi] = events.get(hi, 0) - 1
    result, count, start = [], 0, None
    for point in sorted(events):
        before = count
        count += events[point]
        if before == 0 and count > 0:
            start = point
        if before > 0 and count == 0:
            result.append((start, point))
    return result
