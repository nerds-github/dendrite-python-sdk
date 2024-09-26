import pytest
import asyncio

import pytest_asyncio
from dendrite_sdk.async_api._core.dendrite_browser import (
    AsyncDendrite,
)  # Import your class here


@pytest_asyncio.fixture(scope="session")
async def dendrite_browser():
    """
    Initializes a single instance of AsyncDendrite to be shared across multiple test cases.

    The fixture has a session scope, so it will only be initialized once for the entire test session.
    """
    async with AsyncDendrite(
        openai_api_key="your_openai_api_key",
        dendrite_api_key="your_dendrite_api_key",
        anthropic_api_key="your_anthropic_api_key",
    ) as browser:
        yield browser  # Provide the browser to tests