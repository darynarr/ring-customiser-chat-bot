import os
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
from src.writer import save_to_csv

DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

docs = {
    "customizations": DATA_DIR / "customization.md",
    "faq": DATA_DIR / "FAQ.md",
}

output_paths = {Ring: OUTPUT_DIR / "rings.csv", SupportRequest: OUTPUT_DIR / "requests.csv"}

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
        save_to_csv(ai_response, output_paths[Ring], session_id=runner.session_id)
        ai_response = RING_CONFIRMATION_TEMPLATE.format(ring=pydantic_to_text(ai_response))
    elif isinstance(ai_response, SupportRequest):
        save_to_csv(ai_response, output_paths[SupportRequest], session_id=runner.session_id)
        ai_response = SUPPORT_REQUEST_CONFIRMATION_TEMPLATE.format(
            ring=pydantic_to_text(ai_response)
        )
    await cl.Message(content=ai_response).send()
