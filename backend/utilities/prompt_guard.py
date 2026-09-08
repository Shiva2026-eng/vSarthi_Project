import re
from typing import List

# Max characters allowed from document to prevent context overflow / DoS attacks
MAX_DOCUMENT_CHARS = 50000

# Patterns commonly used in prompt injection / jailbreak attempts
INJECTION_PATTERNS = [
    r"(?i)\bignore\s+(all\s+)?(previous|above|prior)\s+(instructions|prompts|directions|rules)\b",
    r"(?i)\bdisregard\s+(all\s+)?(previous|above|prior)\s+(instructions|prompts|directions|rules)\b",
    r"(?i)\bforget\s+(all\s+)?(previous|above|prior)\s+(instructions|prompts|directions|rules)\b",
    r"(?i)\byou\s+are\s+now\s+(a|an|the|in)\b",
    r"(?i)\bsystem\s+override\b",
    r"(?i)\bnew\s+system\s+prompt\b",
    r"(?i)\breveal\s+(the\s+)?(system\s+prompt|instructions)\b",
    r"(?i)\boutput\s+only\s+the\s+following\s+json\b",
    r"(?i)<\s*/?\s*system\s*>",
    r"(?i)<\s*/?\s*assistant\s*>",
    r"(?i)<\s*/?\s*user\s*>",
]


def sanitize_document_text(text: str, max_chars: int = MAX_DOCUMENT_CHARS) -> str:
    """
    Sanitize raw extracted document text:
    - Remove null bytes and non-printable control characters (except common whitespace).
    - Limit length to prevent context exhaustion attacks.
    """
    if not text:
        return ""

    # Strip null bytes
    sanitized = text.replace("\x00", "")

    # Remove non-printable control characters except newline, tab, and carriage return
    sanitized = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", "", sanitized)

    # Truncate if exceeds max_chars
    if len(sanitized) > max_chars:
        sanitized = sanitized[:max_chars] + "\n\n[... Document truncated due to length limits ...]"

    return sanitized


def detect_suspicious_patterns(text: str) -> List[str]:
    """
    Scan text for common prompt injection patterns.
    """
    matches = []
    for pattern in INJECTION_PATTERNS:
        found = re.findall(pattern, text)
        if found:
            matches.append(pattern)
    return matches


def wrap_untrusted_content(text: str, tag_name: str = "untrusted_document_data") -> str:
    """
    Safely encapsulates untrusted document content inside boundary tags.
    Escapes any occurrences of the tag inside the document text to prevent delimiter-closing breakouts.

    Returns:
        wrapped_text: String wrapped in delimiter tags.
    """
    opening_tag = f"<{tag_name}>"
    closing_tag = f"</{tag_name}>"

    # Neutralize closing and opening tags in raw text to prevent breakout
    safe_text = re.sub(rf"(?i)<\s*/?\s*{tag_name}[^>]*>", "[DELIMITER_ESCAPED]", text)

    return f"{opening_tag}\n{safe_text}\n{closing_tag}"
