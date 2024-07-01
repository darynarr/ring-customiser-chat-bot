from enum import Enum

from langchain.pydantic_v1 import BaseModel


def pydantic_to_text(pydantic_object: BaseModel) -> str:
    """
    Convert pydantic object to markdown.

    Args:
        pydantic_object (BaseModel): Pydantic object to convert.

    Returns:
        str: Markdown text.
    """
    text = []
    for key, value in pydantic_object.dict().items():
        if isinstance(value, Enum):
            value = value.value
        text.append(f"**{key.replace('_', ' ').title()}**: {value}")

    return "\n".join(text)
