"""
Module containing class for list of batches.
"""
import os

DEFAULT_BATCH_SIZE = "50"

class BatchList:
    """List of lists with defined maximum size of inner lists."""

    def __init__(self):
        self.max_batch_size = int(os.getenv('BATCH_SIZE', DEFAULT_BATCH_SIZE))
        self.batches = []

    def __iter__(self):
        return iter(self.batches)

    def clear(self):
        """Clear all previously added items."""
        self.batches = []

    def add_item(self, item):
        """Add item into the last batch. Create new batch if there is no batch or last batch is full."""
        if self.batches:
            last_batch = self.batches[-1]
        else:
            last_batch = None
        if last_batch is None or len(last_batch) >= self.max_batch_size:
            last_batch = []
            self.batches.append(last_batch)
        last_batch.append(item)

    def get_total_items(self):
        """Return total item count in all batches."""
        return sum(len(l) for l in self.batches)
