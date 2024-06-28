import uuid
from operator import itemgetter
from pathlib import Path
from typing import Dict, Optional

from langchain.output_parsers import EnumOutputParser
from langchain.schema.output_parser import StrOutputParser
from langchain.vectorstores import DocArrayInMemorySearch
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import TextLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnableParallel
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

from src.prompts import (
    CUSTOMIZATION_PROMPT,
    FAQ_PROMPT,
    RING_PROMPT,
    ROUTER_PROMPT,
    SUPPORT_PROMPT,
    create_prompt,
)
from src.schemas import Ring, SupportRequest, Topic


class Config:
    MODEL = "gpt-3.5-turbo"
    TEMPERATURE = 0


PROMPTS_BY_TOPIC = {
    Topic.CUSTOMIZATION: CUSTOMIZATION_PROMPT,
    Topic.RING: RING_PROMPT,
    Topic.REQUEST: SUPPORT_PROMPT,
    Topic.FAQ: FAQ_PROMPT,
}


class Runner:
    def __init__(self, docs: Dict[str, Path]):
        self.docs = docs
        self.store = {}
        self.session_id = None

    def setup(self):
        self.session_id = uuid.uuid4()

        retrieval = self.get_retrieval_chain()
        router = self.get_router_chain()
        branch = self.get_branch_chain()

        chain = retrieval | router | branch
        self.with_message_history = RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def __call__(self, message: str):
        return self.with_message_history.invoke(
            {"input": message},
            config={"configurable": {"session_id": self.session_id}},
        )

    def get_session_history(self, session_id) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

    def get_retrieval_chain(self):
        retrievers = {name: self.get_retriever(path) for name, path in self.docs.items()}
        context = {
            f"context_{name}": RunnableLambda(itemgetter("input")) | retriever for name, retriever in retrievers.items()
        }
        retrieval = RunnableParallel(
            {
                **context,
                "input": itemgetter("input"),
                "history": itemgetter("history"),
            }
        )
        return retrieval

    @staticmethod
    def get_retriever(filepath: Path, splitter_kwargs: Optional[Dict] = None, search_kwargs: Optional[Dict] = None):
        # Set default params if None was given
        splitter_kwargs = splitter_kwargs or dict(chunk_size=200, chunk_overlap=0)
        search_kwargs = search_kwargs or {"k": 2}

        loader = TextLoader(file_path=filepath, encoding="utf-8")
        documents = loader.load()
        text_splitter = CharacterTextSplitter(**splitter_kwargs)
        docs = text_splitter.split_documents(documents)

        embedding_model = OpenAIEmbeddings()
        vectorstore_customizations = DocArrayInMemorySearch.from_documents(docs, embedding_model)

        retriever = vectorstore_customizations.as_retriever(search_kwargs=search_kwargs)
        return retriever

    def get_router_chain(self):
        router_prompt_str = ROUTER_PROMPT.replace(
            "{format_instructions}", EnumOutputParser(enum=Topic).get_format_instructions()
        )
        router_prompt = create_prompt(router_prompt_str, include_history=False)
        router_parser = StrOutputParser()

        llm = ChatOpenAI(model=Config.MODEL, temperature=Config.TEMPERATURE)

        router_chain = {
            **{f"context_{name}": itemgetter(f"context_{name}") for name in self.docs.keys()},
            "input": itemgetter("input"),
            "history": itemgetter("history"),
            "topic": router_prompt | llm | router_parser,
        }
        return router_chain

    def get_branch_chain(self):
        llm = ChatOpenAI(model=Config.MODEL, temperature=Config.TEMPERATURE)

        branches = {
            Topic.CUSTOMIZATION: create_prompt(CUSTOMIZATION_PROMPT) | llm | StrOutputParser(),
            Topic.RING: (
                create_prompt(RING_PROMPT)
                | llm.bind(response_format={"type": "json_object"})
                | JsonOutputParser(pydantic_object=Ring)
            ),
            Topic.REQUEST: (
                create_prompt(SUPPORT_PROMPT)
                | llm.bind(response_format={"type": "json_object"})
                | JsonOutputParser(pydantic_object=SupportRequest)
            ),
            Topic.FAQ: create_prompt(FAQ_PROMPT) | llm | StrOutputParser(),
        }

        branch_chain = RunnableBranch(
            *[(lambda x: topic in x["topic"].lower(), branch) for topic, branch in branches.items()],
            branches[Topic.FAQ],  # General chain
        )
        return branch_chain
