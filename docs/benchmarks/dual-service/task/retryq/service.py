from datetime import timedelta
from .policy import retry_delay


class RetryService:
    def __init__(self, queue):
        self.queue = queue

    def fail(self, tenant, job_id, payload, attempt, now, status,
             retry_after=None, base=1, cap=60):
        if status < 500:
            return False
        delay = retry_delay(attempt, now, base, cap, retry_after)
        self.queue.enqueue(tenant, job_id, payload, now + timedelta(seconds=delay))
        return True
