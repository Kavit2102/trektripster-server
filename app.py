from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from database.connection import DatabaseConnection
from services.trektripster import TrekTripster
# from database.conversation import Conversation
from routers import chat

# DATABASE_file_name = "database.db"
# DATABASE_url = f"sqlite:///{DATABASE_file_name}"

origins = [
    "http://localhost:3000",    # React local development
    "http://localhost:5173",    # Vite local development
    "https://trektripster-ui.vercel.app",   # Production domain
]

database = DatabaseConnection()
trek_tripster = TrekTripster()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database = database
    app.state.trek_tripster = trek_tripster

    database.create_tables()

    yield

    database.dispose()

app = FastAPI(
    title="trektripster-server",
    description="API for answering queries based on uploaded documents",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allows requests from specified origins
    allow_credentials=True,           # Allows cookies and credentials
    allow_methods=["*"],              # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],              # Allows all request headers
)

@app.get("/")
def home():
    return {"message": "TrekTripster Server is running"}

app.include_router(
    chat.create_router(
        database=database,
        trek_tripster=trek_tripster,
    )
)