# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import asyncio

from collections.abc import AsyncIterator
from typing import TypeVar

T = TypeVar('T')

def format_sse_event(event: str, data: str | None = None) -> str:
    """SSE(Server-Sent Events) 메시지를 문자열로 포맷팅합니다.

    Args:
        event (str): 이벤트 이름
        data (Optional[str], optional): 이벤트 데이터. Defaults to None.

    Returns:
        str: SSE 프로토콜에 맞게 포맷팅된 메시지 문자열
    """
    sse_lines = [f"event: {event}"]
    if data is not None:
        sse_lines.append(f"data: {data}")
    return "\n".join(sse_lines) + "\n\n"


async def wrap_stream_with_timeout(
    streamer: AsyncIterator[T],
    timeout_seconds: int = 60
) -> AsyncIterator[T]:
    stream_iterator = streamer.__aiter__()

    while True:
        try:
            resp = await asyncio.wait_for(
                stream_iterator.__anext__(),
                timeout=timeout_seconds
            )

            yield resp
        except StopAsyncIteration:
            break

        except TimeoutError as e:
            raise TimeoutError(
                f"스트림 응답 대기 시간이 {timeout_seconds}초를 초과했습니다."
            ) from e
