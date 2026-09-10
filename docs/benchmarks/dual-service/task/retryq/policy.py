def retry_delay(attempt, now, base=1, cap=60, retry_after=None):
    delay = min(cap, base * 2 ** attempt)
    if retry_after is not None:
        try:
            delay = float(retry_after)
        except ValueError:
            pass
    return delay
