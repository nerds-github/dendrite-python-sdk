import sys
from loguru import logger
from dendrite_sdk.async_api import (
    AsyncDendrite,
    AsyncElement,
    AsyncPage,
    AsyncElementsResponse,
)

from dendrite_sdk.sync_api import (
    Dendrite,
    Element,
    Page,
    ElementsResponse,
)

logger.remove()

fmt = "<green>{time: HH:mm:ss.SSS}</green> | <level>{level: <8}</level>- <level>{message}</level>"

logger.add(sys.stderr, level="WARNING", format=fmt)


__all__ = [
    "AsyncDendrite",
    "AsyncElement",
    "AsyncPage",
    "AsyncElementsResponse",
    "Dendrite",
    "Element",
    "Page",
    "ElementsResponse",
]
