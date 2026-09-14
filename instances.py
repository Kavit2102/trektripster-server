# export QdrantClient instance to be used in other modules
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
import os
# import psycopg

qdrantClient = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

collection = os.getenv("COLLECTION_NAME", "trektripster")
