import uuid
from operator import itemgetter
from pathlib import Path
from typing import Dict, Optional, Union

from langchain.output_parsers import EnumOutputParser
from langchain.schema.output_parser import StrOutputParser
from langchain.vectorstores import DocArrayInMemorySearch
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import TextLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnableParallel
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.vectorstores import VectorStoreRetriever
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


class Conversation:
    """
    This class is used to run a conversation with the user. It classifies each input from the user
    to use the most appropriate chain to get a response.
    """

    def __init__(self, docs: Dict[str, Path]):
        """
        Initialize conversation.

        Args:
            docs (Dict[str, Path]): Pathes to documents by the names.
        """
        self.docs = docs
        self.store = {}
        self.session_id = None

    def setup(self):
        """
        Bring all the chains together and set up new conversation session.
        """
        self.session_id = str(uuid.uuid4())

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

    def __call__(self, message: str) -> Union[str, dict]:
        """
        Pass the input to conversation to get the response from the model.

        Args:
            message (str): Text input.

        Returns:
            Union[str, dict]: Text or somewhat structured output.
        """
        return self.with_message_history.invoke(
            {"input": message},
            config={"configurable": {"session_id": self.session_id}},
        )

    def get_session_history(self, session_id: str) -> ChatMessageHistory:
        """
        Get conversation history by the session, create if needed.

        Args:
            session_id (str): Id of the session to get history for.

        Returns:
            ChatMessageHistory: Session history.
        """
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

    def get_retrieval_chain(self) -> RunnableParallel:
        """
        Set up retrieval chain: create a retriever for each documents.

        Returns:
            RunnableParallel: Retrieval chain.
        """
        retrievers = {name: self.get_retriever(path) for name, path in self.docs.items()}
        context = {
            f"context_{name}": RunnableLambda(itemgetter("input")) | retriever
            for name, retriever in retrievers.items()
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
    def get_retriever(
        filepath: Path,
        splitter_kwargs: Optional[Dict] = None,
        search_kwargs: Optional[Dict] = None,
    ) -> VectorStoreRetriever:
        """
        Create retriever for the text document.

        Args:
            filepath (Path): Path to the document.
            splitter_kwargs (Optional[Dict], optional): Parameters for text splitter. Defaults to None.
            search_kwargs (Optional[Dict], optional): Parameters for search. Defaults to None.

        Returns:
            VectorStoreRetriever: Retriever for the document.
        """
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

    def get_router_chain(self) -> RunnableParallel:
        """
        Set up router chain: this chain classifies the topic of the input to further pass it to the
        correct branch chain.

        Returns:
            RunnableParallel: Router chain.
        """
        router_prompt_str = ROUTER_PROMPT.replace(
            "{format_instructions}",
            EnumOutputParser(enum=Topic).get_format_instructions(),
        )
        router_prompt = create_prompt(router_prompt_str, include_history=False)

        llm = ChatOpenAI(model=Config.MODEL, temperature=Config.TEMPERATURE)

        router_chain = RunnableParallel(
            {
                **{f"context_{name}": itemgetter(f"context_{name}") for name in self.docs.keys()},
                "input": itemgetter("input"),
                "history": itemgetter("history"),
                "topic": router_prompt | llm | StrOutputParser(),
            }
        )
        return router_chain

    def get_branch_chain(self) -> RunnableBranch:
        """
        Set up branch chain: selects the correct branch to use based on topic defined by router chain.

        Returns:
            RunnableBranch: Branch chain.
        """
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
            *[
                (
                    lambda x, topic=topic: topic in x["topic"].lower(),
                    branches[topic],
                )
                for topic in branches
            ],
            branches[Topic.FAQ],  # General chain
        )

        return branch_chain
