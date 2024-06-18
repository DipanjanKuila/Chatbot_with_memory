from fastapi import FastAPI, HTTPException
from typing import Optional, List
from pydantic import BaseModel
import os

from chatbot import (
    get_function,
    fetch_chat_history,
    display_conversation,
    generate_conversation_title,
    display_recent_conversations,
    delete_conversation,
)

app = FastAPI()

class QueryRequest(BaseModel):
    conversation_id: Optional[int] = None
    query: Optional[str] = None

@app.post("/query/")
async def ask_question(request_data: QueryRequest):
    conversation_id = request_data.conversation_id
    query = request_data.query
    response = get_function(conversation_id, query)

    if "previous_conversations" in response:
        return {"previous_conversations": response["previous_conversations"]}
    elif "conversation_id" not in response and "answer" not in response:
        raise HTTPException(status_code=400, detail="Invalid request. Please provide a query or a conversation_id.")

    return response

@app.get("/conversation/{conversation_id}")
async def get_conversation_history(conversation_id: int):
    chat_history = fetch_chat_history(conversation_id)
    conversation = display_conversation(chat_history)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    return {"conversation_history": conversation}

@app.get("/previous-conversations")
async def get_previous_conversations():
    recent_conversations = display_recent_conversations()
    previous_conversations = []

    for conversation_id in recent_conversations[:10]:
        chat_history = fetch_chat_history(conversation_id)
        title = generate_conversation_title(conversation_id,chat_history)
        previous_conversations.append({"conversation_id": conversation_id, "title": title})

    return {"previous_conversations": previous_conversations}

@app.delete("/conversation/{conversation_id}")
async def delete_conversation_endpoint(conversation_id: int):
    try:
        delete_conversation(conversation_id)
        return {"message": f"Conversation ID {conversation_id} has been deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)