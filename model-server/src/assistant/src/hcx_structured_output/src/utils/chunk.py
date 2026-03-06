# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# src/utils/chunk.py
import re
from typing import List

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def split_text(text: str, max_chars: int = 400) -> List[str]:
    sentences = [s.strip() for s in _SENT_SPLIT.split(text) if s.strip()]
    parts: List[str] = []
    buf: List[str] = []
    cur_len = 0  # length of buf joined by space

    def flush():
        nonlocal buf, cur_len
        if buf:
            parts.append(" ".join(buf).strip())
            buf = []
            cur_len = 0

    for s in sentences:
        piece = s  # original text, no forced period
        add_len = (1 if buf else 0) + len(piece)  # include 1 space
        if cur_len + add_len > max_chars:
            flush()
        if buf:
            buf.append(piece)
            cur_len += 1 + len(piece)  # space + content
        else:
            buf.append(piece)
            cur_len += len(piece)

    flush()
    return parts
