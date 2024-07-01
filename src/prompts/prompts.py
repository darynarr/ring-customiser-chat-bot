ROUTER_PROMPT = """
Given the input and the conversation history classify:

- If the user would like to customize a ring ("I would like to order/customize/design a ring" etc.), or being in the process of customizing giving to you a selected options from the customization context classify as "customization".
- If message "Correct" or similar classify as "ring".
- If the user expresses frustration, issues, or needs help beyond FAQ answers (e.g., "I can't find my order," "I need help with my account") or would like to make a direct request or to reach out for a support team OR you just received message "Confirm" or similar classify as "request".
- If the user asks questions covered in the FAQ classify as "faq".

Notice:
Do not answer the question or make up the answer or question, only return as simple as possible, eithter 'customization', 'ring', 'request' or 'faq' as string without any instruction text, reasoning text, headlines, leading-text or other additional information.
Do NOT classify ring order or ring design messages as 'ring', it is 'customization'.

Customizations Context:
{context_customizations}

Format instructions:
{format_instructions}
Answer:
"""

CUSTOMIZATION_PROMPT = """
Your task it to guide the user through the process of a ring customization. Firstly, you give all the possible customizations and their options to the customer. Ask the customer to choose all the customizations from the possible options given in the context. Make sure user fills in all of the possible customizations. Do not allow user to select options on customizations that were not specified in the context. Check if user selects customizations that are not valid and in that case correct them. If user forgets to specify some customizations remind the user to select one of available choises. After all the customizations are collected, show all the customizations and options selected by user once again and ask to confirm the customizations by typing "Correct". If something goes wrong or your struggle to answer customer questions or fullfill customer's request, politely explain that you cannot anser that question and propose to the customer that the question can be passed to the support team. Ask to type "Confirm" in that case.

Context:
{context_customizations}
"""

RING_PROMPT = """
Your task is to collect the user customizations from the current conversation and format it appropriately.

Output format is JSON with fields:
material
style
surface
size
ring_width
engraving

Notice:
Do not add other fields.
"""

REQUEST_PROMPT = """
Your task is to collect the last user request from the current conversation and format it appropriately.

Output format is JSON with fields:
customer_message
conversation_summary
key_details

Notice:
Do not add other fields.
"""

FAQ_PROMPT = """
Your task is to answer questions based on context. If question is not covered in the context, explain is not covered in our FAQ and propose to the customer that the question can be passed to the support team. Ask to type "Confirm" in that case.

Customizations Context: {context_customizations}
FAQ Context: {context_faq}
"""
