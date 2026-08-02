from enum import Enum


class SourceEnum(str, Enum):
    """Source from which a document was ingested."""

    MANUAL = "manual"
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"


class StatusEnum(str, Enum):
    """Current processing status of a document."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    DELETED = "deleted"
