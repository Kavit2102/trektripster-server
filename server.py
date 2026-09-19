from uuid import uuid4
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import DatabaseConnection
from database.conversation import Conversation
from trektripster import TrekTripster
from database.message import Message
import asyncio

# DATABASE_file_name = "database.db"
# DATABASE_url = f"sqlite:///{DATABASE_file_name}"

app = FastAPI(title="trektripster-server", description="API for answering queries based on uploaded documents")

origins = [
    "http://localhost:3000",    # React local development
    "http://localhost:5173",    # Vite local development
    "https://trektripster-ui.vercel.app",   # Production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allows requests from specified origins
    allow_credentials=True,           # Allows cookies and credentials
    allow_methods=["*"],              # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],              # Allows all request headers
)

class QuestionRequest(BaseModel):
    question: str
    # user_id: str

# Creates the main trip-answering object used to answer user questions.
trek_tripster = TrekTripster()
# Creates a semantic cache object that can compare similarity and reuse prior answers.

async def answer_and_persist(
    database: DatabaseConnection,
    conversation_id,
    query: str,
):
    # Creates a message service object for working with stored messages.
    message_service = Message(database)

    # Starts a background task that saves the user's original prompt in the DB
    # with an empty content field before the answer is generated.
    create_task = asyncio.create_task(
        asyncio.to_thread(
            message_service.create_message,
            user_id="",
            conversation_id=conversation_id,
            query=query,
            content="",
        )
    )

    # Starts another background task to call the AI answer function for the question.
    answer_task = asyncio.create_task(
        asyncio.to_thread(trek_tripster.answer_question, query)
    )

    # Waits for both tasks to finish and stores both the message record and answer.
    message, answer = await asyncio.gather(create_task, answer_task)

    # Updates the saved message with the final answer produced by the assistant.
    await asyncio.to_thread(
        message_service.update_message,
        message_id=message.message_id,
        content=answer,
    )

    # Returns the generated answer so the caller can print it to the console.
    return answer

@app.get("/")
def home():
    return {"message": "TrekTripster Server is running"}

@app.post("/chat-document")
async def ask_question(request: QuestionRequest):
    if not request.question.strip():
        return {"error": "Question cannot be empty"}

    database = DatabaseConnection()
    database.create_tables()

    conversation_service = Conversation(database)
    conversations = conversation_service.get_conversation(user_id="")

    if conversations:
        conversation_id = conversations[0].conversation_id
    else:
        conversation_id = uuid4()
        conversation_service.create_conversation(
            user_id="",
            conversation_id=conversation_id,
            title="New Convo",
        )

    answer = await answer_and_persist(
        database=database,
        conversation_id=conversation_id,
        query=request.question,
    )

    return {"answer": answer}