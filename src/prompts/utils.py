from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_prompt(prompt_str, include_history=True):
    messages = [("system", prompt_str)]
    if include_history:
        messages.append(MessagesPlaceholder(variable_name="history"))
    messages.append(("human", "{input}"))

    return ChatPromptTemplate.from_messages(messages)
