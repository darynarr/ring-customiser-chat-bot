from pathlib import Path

import chainlit as cl

from src import Conversation

DATA_DIR = Path("data")

docs = {
    "customizations": DATA_DIR / "customization.md",
    "faq": DATA_DIR / "FAQ.md",
}

runner = Conversation(docs)
runner.setup()


@cl.on_message
async def main(message: cl.Message):
    ai_response = runner(message.content)
    await cl.Message(content=ai_response).send()
