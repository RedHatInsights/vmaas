DEFAULT_BATCH_SIZE = 100


class BatchList:
    """List of lists with defined maximum size of inner lists."""

    def __init__(self, max_batch_size=DEFAULT_BATCH_SIZE):
        self.max_batch_size = max_batch_size
        self.batches = []

    def __iter__(self):
        return iter(self.batches)

    def clear(self):
        self.batches = []

    def add_item(self, item):
        if len(self.batches) > 0:
            last_batch = self.batches[-1]
        else:
            last_batch = None
        if last_batch is None or len(last_batch) >= self.max_batch_size:
            last_batch = []
            self.batches.append(last_batch)
        last_batch.append(item)
