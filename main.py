from pathlib import Path

import chainlit as cl

from src import Conversation
from src.messages import (
    RING_CONFIRMATION_TEMPLATE,
    SUPPORT_REQUEST_CONFIRMATION_TEMPLATE,
    WELCOME_MESSAGE,
    pydantic_to_text,
)
from src.schemas import Ring, SupportRequest

DATA_DIR = Path("data")

docs = {
    "customizations": DATA_DIR / "customization.md",
    "faq": DATA_DIR / "FAQ.md",
}

runner = Conversation(docs)
runner.setup()


@cl.on_chat_start
async def on_chat_start():
    runner.get_session_history(runner.session_id).add_ai_message(WELCOME_MESSAGE)
    await cl.Message(content=WELCOME_MESSAGE).send()


@cl.on_message
async def main(message: cl.Message):
    ai_response = runner(message.content)
    if isinstance(ai_response, Ring):
        ai_response = RING_CONFIRMATION_TEMPLATE.format(ring=pydantic_to_text(ai_response))
    elif isinstance(ai_response, SupportRequest):
        ai_response = SUPPORT_REQUEST_CONFIRMATION_TEMPLATE.format(
            ring=pydantic_to_text(ai_response)
        )
    await cl.Message(content=ai_response).send()
