from pydantic import BaseModel
from dendrite_sdk.async_api._core.models.page_information import PageInformation


class PageDiffInformation(BaseModel):
    page_before: PageInformation
    page_after: PageInformation