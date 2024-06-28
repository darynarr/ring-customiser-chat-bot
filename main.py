from pathlib import Path

from src import Runner

DATA_DIR = Path("data")

docs = {
    "customizations": DATA_DIR / "customization.md",
    "faq": DATA_DIR / "FAQ.md",
}

runner = Runner(docs)
runner.setup()

if __name__ == "__main__":
    while True:
        human_message = input("Human: ")
        ai_response = runner(human_message)
        print("AI: ", ai_response)
