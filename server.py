from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from trektripster import TrekTripster
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)


DATABASE_file_name = "database.db"
DATABASE_url = f"sqlite:///{DATABASE_file_name}"

app = FastAPI(title="trektripster-server", description="API for answering queries based on uploaded documents")

origins = [
    "http://localhost:3000",    # React local development
    "http://localhost:5173",    # Vite local development
    "https://yourdomain.com",   # Production domain
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

@app.get("/")
def home():
    return {"message": "TrekTripster Server is running"}

@app.post("/chat-document")
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        return {"error": "Question cannot be empty"}

    answer = TrekTripster().answer_question(request.question)

    return answer