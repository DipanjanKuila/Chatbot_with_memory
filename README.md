# Chatbot_with_memory
I'm developing a chatbot with memory using LangChain. In this project, I am storing all chat history in a local database and have created endpoints using FastAPI.
# Chatbot with Azure OpenAI and SQLAlchemy

Welcome to the Chatbot project, an intelligent conversation agent built using Azure OpenAI's GPT and SQLAlchemy for managing chat history. The chatbot supports starting new conversations, storing messages, fetching conversation history, generating titles for conversations, displaying recent conversations, and deleting conversations.

## Features

- **Start new conversations**
- **Store messages**: Save human and AI messages with timestamps.
- **Fetch chat history**: Retrieve all messages in a conversation.
- **Generate conversation titles**: Automatically create meaningful titles.
- **Display conversation history**: Present chat history in a structured format.
- **Display recent conversations**: Show the IDs of the latest conversations.
- **Delete conversations**: Remove conversations from the history.

## Prerequisites

- Python 3.8 or higher
- Azure OpenAI account with API key and endpoint
- SQLite (included with Python)

# FastAPI Chatbot API

This project is a FastAPI-based chatbot API that provides endpoints for querying a chatbot, retrieving conversation histories, displaying recent conversations, and deleting conversations.

## Features

- **Query the Chatbot**: Send a query to the chatbot and get a response.
- **Get Conversation History**: Retrieve the history of a specific conversation.
- **Get Previous Conversations**: List the last 10 conversations with their titles.
- **Delete Conversation**: Delete a specific conversation by its ID.

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn
- Pydantic

## Payload for Query Endpoint

### Creating a New Conversation
To create a new conversation, send the following payload:
{
  "query": "hello how are you"
}

### Using an Existing Conversation
To continue an existing conversation, send the following payload:

{
  "conversation_id": 1,
  "query": "hello how are you"
}





