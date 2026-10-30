"""Load the user-approved fictional records into an isolated practice session."""
from services.core import KINDS, Store


def initialize_demo(destination, sample_root):
    # Read every collection through Store so invalid records fail before any write.
    source=Store(sample_root)
    records={kind:source.load(kind) for kind in KINDS}
    # Each visitor gets a private working copy; the committed demo stays unchanged.
    for kind,rows in records.items():
        destination.save(kind,rows)
