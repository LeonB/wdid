class Task:
    start_time = None
    end_time = None
    identifier = None
    project = None
    uris = set()
    reason = ''

    def duration(self):
        return self.end_time - self.start_time
