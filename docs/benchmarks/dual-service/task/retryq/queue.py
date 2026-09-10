class RetryQueue:
    def __init__(self):
        self.jobs = {}

    def enqueue(self, tenant, job_id, payload, due_at):
        self.jobs[job_id] = {'tenant': tenant, 'job_id': job_id,
                             'payload': payload, 'due_at': due_at}

    def pop_due(self, now, limit=100):
        due = [job for job in self.jobs.values() if job['due_at'] < now][:limit]
        for job in due:
            del self.jobs[job['job_id']]
        return due

    def __len__(self):
        return len(self.jobs)
