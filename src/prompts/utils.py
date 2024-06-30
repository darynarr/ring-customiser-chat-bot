from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_prompt(prompt_str: str, include_history: bool = True) -> ChatPromptTemplate:
    """
    This function is creating prompt template.

    Args:
        prompt_str (str): Prompt text.
        include_history (bool, optional): If to add the history to the prompt.
            Defaults to True.

    Returns:
        ChatPromptTemplate: Prompt template.
    """
    messages = [("system", prompt_str)]
    if include_history:
        messages.append(MessagesPlaceholder(variable_name="history"))
    messages.append(("human", "{input}"))

    return ChatPromptTemplate.from_messages(messages)
