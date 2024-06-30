from typing import Annotated

from langchain.pydantic_v1 import BaseModel, Field


class SupportRequest(BaseModel):
    """
    Support request schema.
    """

    customer_message: Annotated[
        str,
        Field(description="The message from the customer"),
    ]
    conversation_summary: Annotated[
        str,
        Field(description="Summary of the current conversation with the customer"),
    ]
    key_details: Annotated[
        str,
        Field(description="Key details of request or struggle"),
    ]
