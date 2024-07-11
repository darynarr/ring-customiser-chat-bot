# ring-customiser-chat-bot
# Customizable Rings Conversational Agent

## Task Overview

The task is to implement a conversational agent using open-source tools for a virtual platform selling customizable rings.

**RingDesigner** is a made-up platform where users can design and order customizable rings. The created chatbot should assist users with selecting styles, sizes, and engraving options, answer FAQs, and log support requests.

## Objectives

The goal is to build a chatbot that can:

1. **Collect user orders for a customizable ring:**
   - Guide users through style, size, surface, width, and engraving options.
   - Collect all necessary details.

2. **Answer user questions using FAQs:**
   - Provide factual and extensive answers.

3. **Send support requests:**
   - Detect user struggles or direct requests and capture key details for the support team.

The chatbot should be integrated with a chat interface (i.e., Chainlit).

## Provided Documents

You will be provided with the following documents:
1. **Document on Ring Customization**
2. **FAQ Document**

## How to run
Create a `.env` file in your repository directory with the following content:
```
OPENAI_API_KEY=your_openai_api_key
OPENAI_ORGANIZATION=your_openai_organization
```
Replace `your_openai_api_key` and `your_openai_organization` with your actual OpenAI credentials.

Then run with docker:
```
docker build -t ring-customizer .
docker run -p 8001:8001 -v $(pwd)/output:/app/output ring-customizer
```
or with conda:
```
conda create --name ring-customizer python=3.11
conda activate ring-customizer
pip install -r requirements.txt
chainlit run main.py
```
