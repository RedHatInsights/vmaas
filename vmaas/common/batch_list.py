"""
Module containing class for list of batches.
"""
import os

BATCH_MAX_SIZE = int(os.getenv('BATCH_MAX_SIZE', "500"))
BATCH_MAX_FILESIZE = int(os.getenv('BATCH_MAX_FILESIZE', "14_000_000_000"))


class BatchList:
    """List of lists with defined maximum size of inner lists or by arbitrary file_size of each item"""

    def __init__(self):
        self.batches = []
        self.last_batch_filesize = 0

    def __iter__(self):
        return iter(self.batches)

    def clear(self):
        """Clear all previously added items."""
        self.batches = []

    def add_item(self, item, file_size=0):
        """Add item into the last batch. Create new batch if there is no batch or last batch is full."""
        if self.batches:
            last_batch = self.batches[-1]
        else:
            last_batch = None

        assert BATCH_MAX_FILESIZE > file_size, \
            'Single repo uses %d Bytes, which is more than allowed BATCH_MAX_FILESIZE(%d)' \
            % (file_size, BATCH_MAX_FILESIZE)

        if last_batch is None or len(last_batch) >= BATCH_MAX_SIZE \
                or self.last_batch_filesize + file_size > BATCH_MAX_FILESIZE:
            last_batch = []
            self.batches.append(last_batch)
            self.last_batch_filesize = 0

        last_batch.append(item)
        self.last_batch_filesize += file_size

    def get_total_items(self):
        """Return total item count in all batches."""
        return sum(len(batch) for batch in self.batches)
