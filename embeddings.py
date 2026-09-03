from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from qdrant_client.http.models import Distance, VectorParams
from dbinstance import embeddings
import os

def store_embeddings(chunks):
    """
    Store embeddings of document chunks in a Qdrant vector store.

    Args:
        chunks (List[Document]): A list of document chunks to be embedded and stored.
    
    Returns:
        QdrantVectorStore: A Qdrant vector store containing the embeddings.
    """
    
    client = QdrantClient(
        url=os.environ.get("QDRANT_URL"),
        api_key=os.environ.get("QDRANT_API_KEY")
    )

    collections = client.get_collections()

    # Check if the collection already exists, if not, create it
    if not any(collection.name == os.getenv("COLLECTION_NAME", "trektripster") for collection in collections.collections):
        client.create_collection(
            collection_name=os.getenv("COLLECTION_NAME", "trektripster"),
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
        )

    # Store the embeddings in the Qdrant vector store
    vector_store = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        client=client,
        collection_name=os.getenv("COLLECTION_NAME", "trektripster"),
        path=":memory:"
    )

    return vector_store

# embeddings_store = store_embeddings(chunk_documents)

