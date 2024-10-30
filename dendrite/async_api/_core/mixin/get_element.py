import asyncio
import time
from typing import Dict, List, Literal, Optional, Union, overload

from loguru import logger

from dendrite.async_api._api.dto.get_elements_dto import GetElementsDTO
from dendrite.async_api._api.response.get_element_response import GetElementResponse
from dendrite.async_api._api.dto.get_elements_dto import CheckSelectorCacheDTO
from dendrite.async_api._core.dendrite_element import AsyncElement
from dendrite.async_api._core.models.response import AsyncElementsResponse
from dendrite.async_api._core.protocol.page_protocol import DendritePageProtocol
from dendrite.async_api._core.models.api_config import APIConfig


CACHE_TIMEOUT = 5


class GetElementMixin(DendritePageProtocol):
    @overload
    async def get_elements(
        self,
        prompt_or_elements: str,
        use_cache: bool = True,
        timeout: int = 15000,
        context: str = "",
    ) -> List[AsyncElement]:
        """
        Retrieves a list of Dendrite elements based on a string prompt.

        Args:
            prompt_or_elements (str): The prompt describing the elements to be retrieved.
            use_cache (bool, optional): Whether to use cached results. Defaults to True.
            timeout (int, optional): Maximum time in milliseconds for the entire operation. If use_cache=True,
                up to 5000ms will be spent attempting to use cached selectors before falling back to the
                find element agent for the remaining time. Defaults to 15000 (15 seconds).
            context (str, optional): Additional context for the retrieval. Defaults to an empty string.

        Returns:
            List[AsyncElement]: A list of Dendrite elements found on the page.
        """

    @overload
    async def get_elements(
        self,
        prompt_or_elements: Dict[str, str],
        use_cache: bool = True,
        timeout: int = 15000,
        context: str = "",
    ) -> AsyncElementsResponse:
        """
        Retrieves Dendrite elements based on a dictionary.

        Args:
            prompt_or_elements (Dict[str, str]): A dictionary where keys are field names and values are prompts describing the elements to be retrieved.
            use_cache (bool, optional): Whether to use cached results. Defaults to True.
            timeout (int, optional): Maximum time in milliseconds for the entire operation. If use_cache=True,
                up to 5000ms will be spent attempting to use cached selectors before falling back to the
                find element agent for the remaining time. Defaults to 15000 (15 seconds).
            context (str, optional): Additional context for the retrieval. Defaults to an empty string.

        Returns:
            AsyncElementsResponse: A response object containing the retrieved elements with attributes matching the keys in the dict.
        """

    async def get_elements(
        self,
        prompt_or_elements: Union[str, Dict[str, str]],
        use_cache: bool = True,
        timeout: int = 15000,
        context: str = "",
    ) -> Union[List[AsyncElement], AsyncElementsResponse]:
        """
        Retrieves Dendrite elements based on either a string prompt or a dictionary of prompts.

        This method determines the type of the input (string or dictionary) and retrieves the appropriate elements.
        If the input is a string, it fetches a list of elements. If the input is a dictionary, it fetches elements for each key-value pair.

        Args:
            prompt_or_elements (Union[str, Dict[str, str]]): The prompt or dictionary of prompts for element retrieval.
            use_cache (bool, optional): Whether to use cached results. Defaults to True.
            timeout (int, optional): Maximum time in milliseconds for the entire operation. If use_cache=True,
                up to 5000ms will be spent attempting to use cached selectors before falling back to the
                find element agent for the remaining time. Defaults to 15000 (15 seconds).
            context (str, optional): Additional context for the retrieval. Defaults to an empty string.

        Returns:
            Union[List[AsyncElement], AsyncElementsResponse]: A list of elements or a response object containing the retrieved elements.

        Raises:
            ValueError: If the input is neither a string nor a dictionary.
        """

        return await self._get_element(
            prompt_or_elements,
            only_one=False,
            use_cache=use_cache,
            timeout=timeout / 1000,
        )

    async def get_element(
        self,
        prompt: str,
        use_cache=True,
        timeout=15000,
    ) -> Optional[AsyncElement]:
        """
        Retrieves a single Dendrite element based on the provided prompt.

        Args:
            prompt (str): The prompt describing the element to be retrieved.
            use_cache (bool, optional): Whether to use cached results. Defaults to True.
            timeout (int, optional): Maximum time in milliseconds for the entire operation. If use_cache=True,
                up to 5000ms will be spent attempting to use cached selectors before falling back to the
                find element agent for the remaining time. Defaults to 15000 (15 seconds).

        Returns:
            AsyncElement: The retrieved element.
        """
        return await self._get_element(
            prompt,
            only_one=True,
            use_cache=use_cache,
            timeout=timeout / 1000,
        )

    @overload
    async def _get_element(
        self,
        prompt_or_elements: str,
        only_one: Literal[True],
        use_cache: bool,
        timeout,
    ) -> Optional[AsyncElement]:
        """
        Retrieves a single Dendrite element based on the provided prompt.

        Args:
            prompt (Union[str, Dict[str, str]]): The prompt describing the element to be retrieved.
            only_one (Literal[True]): Indicates that only one element should be retrieved.
            use_cache (bool): Whether to use cached results.
            timeout (int, optional): Maximum time in milliseconds for the entire operation. If use_cache=True,
                up to 5000ms will be spent attempting to use cached selectors before falling back to the
                find element agent for the remaining time. Defaults to 15000 (15 seconds).

        Returns:
            AsyncElement: The retrieved element.
        """

    @overload
    async def _get_element(
        self,
        prompt_or_elements: Union[str, Dict[str, str]],
        only_one: Literal[False],
        use_cache: bool,
        timeout,
    ) -> Union[List[AsyncElement], AsyncElementsResponse]:
        """
        Retrieves a list of Dendrite elements based on the provided prompt.

        Args:
            prompt (str): The prompt describing the elements to be retrieved.
            only_one (Literal[False]): Indicates that multiple elements should be retrieved.
            use_cache (bool): Whether to use cached results.
            timeout (int, optional): Maximum time in milliseconds for the entire operation. If use_cache=True,
                up to 5000ms will be spent attempting to use cached selectors before falling back to the
                find element agent for the remaining time. Defaults to 15000 (15 seconds).

        Returns:
            List[AsyncElement]: A list of retrieved elements.
        """

    async def _get_element(
        self,
        prompt_or_elements: Union[str, Dict[str, str]],
        only_one: bool,
        use_cache: bool,
        timeout: float,
    ) -> Union[
        Optional[AsyncElement],
        List[AsyncElement],
        AsyncElementsResponse,
    ]:
        """
        Retrieves Dendrite elements based on the provided prompt, either a single element or a list of elements.

        This method sends a request with the prompt and retrieves the elements based on the `only_one` flag.

        Args:
            prompt_or_elements (Union[str, Dict[str, str]]): The prompt or dictionary of prompts for element retrieval.
            only_one (bool): Whether to retrieve only one element or a list of elements.
            use_cache (bool): Whether to use cached results.
            timeout (int, optional): Maximum time in milliseconds for the entire operation. If use_cache=True,
                up to 5000ms will be spent attempting to use cached selectors before falling back to the
                find element agent for the remaining time. Defaults to 15000 (15 seconds).

        Returns:
            Union[AsyncElement, List[AsyncElement], AsyncElementsResponse]: The retrieved element, list of elements, or response object.
        """

        api_config = self._get_dendrite_browser().api_config
        start_time = time.time()

        # First, let's check if there is a cached selector
        cache_available = await test_if_cache_available(self, prompt_or_elements)

        # If we have cached elements, attempt to use them with an exponentation backoff
        if cache_available and use_cache == True:
            logger.info(f"Cache available, attempting to use cached selectors")
            res = await attempt_with_backoff(
                self,
                prompt_or_elements,
                only_one,
                api_config,
                remaining_timeout=CACHE_TIMEOUT,
                only_use_cache=True,
            )
            if res:
                return res
            else:
                logger.debug(
                    f"After attempting to use cached selectors several times without success, let's find the elements using the find element agent."
                )

        # Now that no cached selectors were found or they failed repeatedly, let's use the find element agent to find the requested elements.
        logger.info(
            "Proceeding to use the find element agent to find the requested elements."
        )
        res = await attempt_with_backoff(
            self,
            prompt_or_elements,
            only_one,
            api_config,
            remaining_timeout=timeout - (time.time() - start_time),
            only_use_cache=False,
        )
        if res:
            return res

        logger.error(
            f"Failed to retrieve elements within the specified timeout of {timeout} seconds"
        )
        return None


async def test_if_cache_available(
    obj: DendritePageProtocol,
    prompt_or_elements: Union[str, Dict[str, str]],
) -> bool:
    page = await obj._get_page()
    page_information = await page.get_page_information(include_screenshot=False)
    dto = CheckSelectorCacheDTO(
        url=page_information.url,
        prompt=prompt_or_elements,
    )
    cache_available = await obj._get_browser_api_client().check_selector_cache(dto)
    return cache_available.exists


async def attempt_with_backoff(
    obj: DendritePageProtocol,
    prompt_or_elements: Union[str, Dict[str, str]],
    only_one: bool,
    api_config: APIConfig,
    remaining_timeout: float,
    only_use_cache: bool = False,
) -> Union[Optional[AsyncElement], List[AsyncElement], AsyncElementsResponse]:
    TIMEOUT_INTERVAL: List[float] = [0.15, 0.45, 1.0, 2.0, 4.0, 8.0]
    total_elapsed_time = 0
    start_time = time.time()

    for current_timeout in TIMEOUT_INTERVAL:
        if total_elapsed_time >= remaining_timeout:
            logger.error(f"Timeout reached after {total_elapsed_time:.2f} seconds")
            return None

        request_start_time = time.time()
        page = await obj._get_page()
        page_information = await page.get_page_information(
            include_screenshot=not only_use_cache
        )
        dto = GetElementsDTO(
            page_information=page_information,
            prompt=prompt_or_elements,
            api_config=api_config,
            use_cache=only_use_cache,
            only_one=only_one,
            force_use_cache=only_use_cache,
        )
        res = await obj._get_browser_api_client().get_interactions_selector(dto)
        request_duration = time.time() - request_start_time

        if res.status == "impossible":
            logger.error(
                f"Impossible to get elements for '{prompt_or_elements}'. Reason: {res.message}"
            )
            return None

        if res.status == "success":
            response = await get_elements_from_selectors(obj, res, only_one)
            if response:
                return response

        sleep_duration = max(0, current_timeout - request_duration)
        logger.info(
            f"Failed to get elements for prompt:\n\n'{prompt_or_elements}'\n\nStatus: {res.status}\n\nMessage: {res.message}\n\nSleeping for {sleep_duration:.2f} seconds"
        )
        await asyncio.sleep(sleep_duration)
        total_elapsed_time = time.time() - start_time

    logger.error(f"All attempts failed after {total_elapsed_time:.2f} seconds")
    return None


async def get_elements_from_selectors(
    obj: DendritePageProtocol, res: GetElementResponse, only_one: bool
) -> Union[Optional[AsyncElement], List[AsyncElement], AsyncElementsResponse]:
    if isinstance(res.selectors, dict):
        result = {}
        for key, selectors in res.selectors.items():
            for selector in selectors:
                page = await obj._get_page()
                dendrite_elements = await page._get_all_elements_from_selector(selector)
                if len(dendrite_elements) > 0:
                    result[key] = dendrite_elements[0]
                    break
        return AsyncElementsResponse(result)
    elif isinstance(res.selectors, list):
        for selector in reversed(res.selectors):
            page = await obj._get_page()
            dendrite_elements = await page._get_all_elements_from_selector(selector)

            if len(dendrite_elements) > 0:
                return dendrite_elements[0] if only_one else dendrite_elements

    return None