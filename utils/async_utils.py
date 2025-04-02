import asyncio
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError

from config import (
    HTTP_MAX_CONCURRENCY,
    HTTP_MAX_RETRIES,
    HTTP_TIMEOUT_CONNECT,
    HTTP_TIMEOUT_SOCK_CONNECT,
    HTTP_TIMEOUT_SOCK_READ,
    HTTP_TIMEOUT_TOTAL,
)
from utils.logger import setup_logger

logger = setup_logger()

# Global session object for reuse during the application lifecycle
_session: Optional[ClientSession] = None


async def get_session() -> ClientSession:
    """
    Get or create a shared aiohttp ClientSession.

    Returns the existing session if available, creating a new one
    if needed. Reusing the session improves performance.

    Returns:
        Shared aiohttp ClientSession instance
    """
    global _session
    if _session is None or _session.closed:
        # Configure timeout settings from environment variables
        timeout = ClientTimeout(
            total=HTTP_TIMEOUT_TOTAL,
            connect=HTTP_TIMEOUT_CONNECT,
            sock_connect=HTTP_TIMEOUT_SOCK_CONNECT,
            sock_read=HTTP_TIMEOUT_SOCK_READ,
        )
        _session = aiohttp.ClientSession(timeout=timeout)
    return _session


async def close_session() -> None:
    """
    Close the shared aiohttp ClientSession.

    This should be called when shutting down the application to
    properly clean up resources.
    """
    global _session
    if _session and not _session.closed:
        await _session.close()
        _session = None


async def fetch_async(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = HTTP_TIMEOUT_TOTAL,
    retries: int = HTTP_MAX_RETRIES,
) -> str:
    """
    Asynchronously fetch content from a URL with retry capability.

    Args:
        url: URL to fetch
        headers: Optional HTTP headers
        timeout: Request timeout in seconds
        retries: Maximum number of retry attempts

    Returns:
        Response text content

    Raises:
        ClientError: On HTTP client error
        asyncio.TimeoutError: On request timeout
        Exception: On other errors
    """
    session = await get_session()

    retry_count = 0
    last_error = None

    while retry_count <= retries:
        try:
            # Increase timeout with each retry
            current_timeout = ClientTimeout(total=timeout * (retry_count + 1))

            async with session.get(url, headers=headers, timeout=current_timeout) as response:
                if response.status >= 400:
                    error_msg = f"HTTP error {response.status}: {url}"
                    logger.warning(error_msg)
                    last_error = ClientError(error_msg)
                    retry_count += 1
                    await asyncio.sleep(1 * retry_count)  # Wait before retrying
                    continue

                return await response.text()

        except (ClientError, asyncio.TimeoutError) as e:
            last_error = e
            logger.warning(f"Request failed ({retry_count+1}/{retries+1}): {url} - {str(e)}")
            retry_count += 1

            if retry_count <= retries:
                # Exponential backoff (1s, 2s, 4s, ...)
                await asyncio.sleep(2 ** (retry_count - 1))
            else:
                break

    # If all retries fail, raise the last error
    if last_error:
        logger.error(f"Maximum retry attempts exceeded: {url}")
        raise last_error

    # Execution should never reach here
    raise Exception(f"Unknown error: {url}")


async def fetch_all_async(
    urls: List[str],
    headers: Optional[Dict[str, str]] = None,
    timeout: int = HTTP_TIMEOUT_TOTAL,
    max_concurrency: int = HTTP_MAX_CONCURRENCY,
) -> List[str]:
    """
    Asynchronously fetch content from multiple URLs with concurrency control.

    Args:
        urls: List of URLs to fetch
        headers: Optional HTTP headers
        timeout: Request timeout in seconds
        max_concurrency: Maximum number of concurrent requests

    Returns:
        List of response texts in the same order as the input URLs
    """
    # Use semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(max_concurrency)

    async def fetch_with_semaphore(url: str) -> str:
        """Fetch a URL with semaphore-controlled concurrency"""
        async with semaphore:
            try:
                return await fetch_async(url, headers, timeout)
            except Exception as e:
                logger.error(f"Failed to fetch URL: {url} - {str(e)}")
                return ""  # Return empty string on error

    # Create tasks for all URLs (limited by semaphore)
    tasks = [fetch_with_semaphore(url) for url in urls]
    return await asyncio.gather(*tasks)


async def fetch_with_timeout(coro: Any, timeout: int) -> Any:
    """
    Run a coroutine with a timeout.

    Args:
        coro: Coroutine to execute
        timeout: Maximum execution time in seconds

    Returns:
        Result of the coroutine execution

    Raises:
        asyncio.TimeoutError: If execution exceeds timeout
    """
    return await asyncio.wait_for(coro, timeout=timeout)
