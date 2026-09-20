from services.semanticcache import SemanticCache
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
import os
from langchain_openai import ChatOpenAI
from infra.collection import collection
from infra.qdrant import qdrantClient
from infra.embeddings import embeddings
from dotenv import load_dotenv

load_dotenv()

class TrekTripster:

    # answer_text: str = ""

    def __init__(self):
        self.retriever = None
        self.cache = SemanticCache(threshold=0.85)
        self.pdf_path = (
            Path(__file__).resolve().parent
            / "docs"
            / "14 to 17 August Special Udaipur Trip.pdf"
        )

        collections = qdrantClient.get_collections()
            
        # Check if the collection already exists, if not, create it
        if not any(collection.name == os.getenv("COLLECTION_NAME") for collection in collections.collections):
            print(f"Creating collection....")
            qdrantClient.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
            )

        print("Collection already exists. Using existing collection")

    def load_documents(self, path):
        loader = PyPDFLoader(path)
        return loader.load()
    
    def chunk_documents(self, documents):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50
        )
        return splitter.split_documents(documents)

    def store_embeddings(self, chunks):
        """
            Store embeddings of document chunks in a QdrantDB store.
        
            Args:
                chunks (List[Document]): A list of document chunks to be embedded and stored.
            
            Returns:
                QdrantDB: A QdrantDB store containing the embeddings.
            """

        # Check if the collection already exists
        collections = qdrantClient.get_collections()
    
        # Check if the collection already exists, if not, create it
        # if not any(collection.name == os.getenv("COLLECTION_NAME") for collection in collections.collections):
        #     qdrantClient.create_collection(
        #         collection_name=os.getenv("COLLECTION_NAME", "trektripster"),
        #         vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
        #     )

        # else:
            # If the collection exists, you can choose to clear it or just use it as is. Here, we will just use it.
        print(f"Collection {os.getenv('COLLECTION_NAME')} already exists. Using existing collection.")

        vector_store = QdrantVectorStore.from_existing_collection(
            embedding=embeddings,
            collection_name=os.getenv("COLLECTION_NAME"),
            api_key=os.getenv("QDRANT_API_KEY"),
            url=os.getenv("QDRANT_URL")
        )

        vector_store.add_documents(chunks) # Add the new chunks to the existing collection

        print("Added to db")
    
        return vector_store

    def get_retrieval(self, embeddings_store):
        return embeddings_store.as_retriever(search_kwargs={"k": 5})

    def generate_answers(self, query, docs):
        """
        Generate answers to a question based on the provided context using the OpenAI model.
    
        Args:
            query (str): The question to be answered.
            docs (List[Document]): The retrieved documents to base the answer on.
    
        Returns:
            str: The generated answer.
        """
    
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
        
        context = "\n\n".join([doc.page_content for doc in docs[:5]])  # Limit to first 5 documents
    
        prompt = f"""
    
                    You are an AI assistant that provides answers to questions based on provided resume. 
        
                    Answer the question based only on the context below.
                    
                    Context: {context}
    
                    Question: {query}
    
                    Answer:
                """
        
        return llm.invoke(prompt)

    def get_rag_pipeline(self):
        if self.retriever is not None:
            return self.retriever

        # Check if the collection exists and has points
        point_count = qdrantClient.count(
            collection_name=collection,
            exact=True,
        ).count

        if point_count == 0:
            print(f"Collection {collection} is empty. Loading documents and storing embeddings...")
            docs = self.load_documents(str(self.pdf_path))
            chunks = self.chunk_documents(docs)
            vector_store = self.store_embeddings(chunks)
        else:
            vector_store = QdrantVectorStore.from_existing_collection(
                embedding=embeddings,
                collection_name=collection,
                api_key=os.getenv("QDRANT_API_KEY"),
                url=os.getenv("QDRANT_URL"),
            )

        self.retriever = self.get_retrieval(vector_store)
        return self.retriever

    def answer_question(self, query):

        cached_answer = self.cache.get_cached_answer(query)
        if cached_answer is not None:
            return cached_answer

        retriever = self.get_rag_pipeline()
        result = retriever.invoke(query)
        answer = self.generate_answers(query, result).content

        # Only write to cache if no close match exists
        self.cache.add_to_cache(query, answer)

        return answer