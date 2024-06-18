
import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, func, text
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from langchain_openai import AzureChatOpenAI
from langchain.memory.buffer import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.schema import HumanMessage, AIMessage
from langchain.prompts import PromptTemplate

GPT_DEPLOYMENT_NAME = "gpt-35-turbo-16k"
os.environ["AZURE_OPENAI_API_KEY"] = "your API key"
os.environ["AZURE_OPENAI_ENDPOINT"] = "your endpoint"
os.environ["OPENAI_API_VERSION"] = "your API version"
llm = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    openai_api_version="your API version",
    azure_deployment=GPT_DEPLOYMENT_NAME,
)

Base = declarative_base()

# Define the Message model
class Message(Base):
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversation.id'), nullable=False)
    role = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    #conversation = relationship("Conversation", back_populates="messages")

class Conversation(Base):
    __tablename__ = 'conversation'
    id = Column(Integer, primary_key=True)
    title = Column(String)  
    #messages = relationship("Message", back_populates="conversation")

engine = create_engine('sqlite:///chat_history.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

'''def start_new_conversation(first_query):
    new_conversation = Conversation()
    session.add(new_conversation)
    session.commit()
    conversation_id = new_conversation.id

    # Get the AI response for the first query
    memory = ConversationBufferMemory(return_messages=True)
    conversation_with_memory = ConversationChain(llm=llm, memory=memory, verbose=True)
    ai_response = conversation_with_memory.predict(input=first_query)

    # Generate the conversation title
    conversation_title = generate_conversation_title(first_query, ai_response)
    new_conversation.title = conversation_title

    # Save the first query and AI response in the chat history
    insert_message(conversation_id, "human", first_query)
    insert_message(conversation_id, "ai", ai_response)

    session.commit()
    return conversation_id'''
   
def start_new_conversation():
    new_conversation = Conversation()
    session.add(new_conversation)
    session.commit()
    return new_conversation.id


def insert_message(conversation_id, role, content):
    message = Message(conversation_id=conversation_id, role=role, content=content)
    session.add(message)
    session.commit()

def fetch_chat_history(conversation_id):
    query = text(f"SELECT role, content FROM chat_history WHERE conversation_id = :conversation_id ORDER BY timestamp")
    chat_history = session.execute(query, {"conversation_id": conversation_id})
    return chat_history.fetchall()

def save_conversation_title(conversation_id, title):
    conversation = session.query(Conversation).get(conversation_id)
    if conversation:
        conversation.title = title
        session.commit()



''''def save_conversation_title(conversation_id, title):
    conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.title = title
        session.commit()'''

def get_first_messages(chat_history):
    human_message = None
    ai_message = None

    for role, content in chat_history:
        if role == "human" and human_message is None:
            human_message = content
        elif role == "ai" and human_message is not None and ai_message is None:
            ai_message = content

        if human_message and ai_message:
            break

    return human_message, ai_message



def generate_conversation_title(conversation_id, chat_history):
    conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation and conversation.title:
        return conversation.title

    
    human_message, ai_message = get_first_messages(chat_history)

    if not human_message or not ai_message:
        return ""

    title_prompt = f"Generate a short, meaningful title for the conversation based on the following human message and AI response: Human: {human_message} AI: {ai_message}"
    title = conversation_with_memory.predict(input=title_prompt)

    save_conversation_title(conversation_id, title)

    return title


def display_conversation(chat_history):
    conversation = []
    for role, content in chat_history:
        if role == "human":
            conversation.append({"role": "user", "content": content})
        elif role == "ai":
            conversation.append({"role": "assistant", "content": content})
    return conversation

def display_recent_conversations():
    query = text("SELECT DISTINCT conversation_id FROM chat_history ORDER BY timestamp DESC LIMIT 5")
    recent_conversations = session.execute(query)
    recent_conversations = [str(row[0]) for row in recent_conversations]
    print("Recent Conversation IDs:")
    print("\n".join(recent_conversations))
    return recent_conversations

def delete_conversation(conversation_id):
    
    query = text(f"DELETE FROM chat_history WHERE conversation_id = :conversation_id")
    session.execute(query, {"conversation_id": conversation_id})
    
    session.commit()

memory = ConversationBufferMemory(return_messages=True)

template = """The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.

Relevant pieces of previous conversation:
{history}

(You do not need to use these pieces of information if not relevant)

Current conversation:
Human: {input}
AI:"""
PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)
conversation_with_memory = ConversationChain(llm=llm, prompt=PROMPT, memory=memory, verbose=True)



def get_function(conversation_id=None, query=""):
    response = {}

    '''if conversation_id is None and query == "":
        recent_conversations = display_recent_conversations()
        response['previous_conversations'] = recent_conversations[:5]'''
    if conversation_id is None and query != "":
        conversation_id = start_new_conversation()
        response['conversation_id'] = conversation_id
    if conversation_id and query:
        chat_history = fetch_chat_history(conversation_id)
        if chat_history:
            # Clear the memory before adding the chat history for the specific conversation_id
            memory.chat_memory.clear()

            
            for role, content in chat_history:
                if role == "human":
                    memory.chat_memory.add_user_message(content)
                elif role == "ai":
                    memory.chat_memory.add_ai_message(content)

        # Add the current query to the memory before generating a response
        memory.chat_memory.add_user_message(query)

        answer = conversation_with_memory.predict(input=query)

        insert_message(conversation_id, "human", query)
        insert_message(conversation_id, "ai", answer)

        response['conversation_id'] = conversation_id
        response['answer'] = answer
        

    return response