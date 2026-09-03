import uuid
import time
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from dbinstance import embeddings, qdrantClient
import os
from logging import Logger

logger = Logger(__name__)

class SemanticCache:
    def __init__(self, threshold=0.70):
        self.encoder = embeddings
        self.cache_client = qdrantClient # Initialize an in-memory Qdrant client for caching
        self.cache_collection_name = "cache"

        if not self.cache_client.collection_exists(self.cache_collection_name):
            self.cache_client.create_collection(
                collection_name=self.cache_collection_name,
                vectors_config=VectorParams(
                    size=3072,
                    distance=Distance.COSINE
                )
            )

        # Initialize Qdrant Client for external database
        self.db_client = QdrantClient(
            os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.db_collection_name = os.getenv('COLLECTION_NAME')
        
        self.threshold = threshold

    def get_embedding(self, question):
        embedding = list(self.encoder.embed_query(question))
        return embedding

    def search_cache(self, embedding):
        # print(f"Searching {embedding}")
        search_result = self.cache_client.query_points(
            collection_name=self.cache_collection_name,
            query = embedding,
            limit=1,
            with_payload=True,
            with_vectors=False
        )
        return search_result.points if search_result else None

    def add_to_cache(self, question, response_text):
        # Create a unique ID for the new point
        point_id = str(uuid.uuid4())
        vector = self.get_embedding(question)
        # Create the point with payload
        point = PointStruct(id=point_id, vector=vector, payload={"response_text": response_text})
        # Upload the point to the cache
        self.cache_client.upload_points(
            collection_name=self.cache_collection_name,
            points=[point]
        )

        logger.info(f"Added to cache: {question} -> {response_text}")
        
    def query_database(self, query_text):
        results = self.db_client.query_points(
            query=self.get_embedding(query_text),
            limit=3,
            collection_name=os.getenv('COLLECTION_NAME'),
            with_payload=True,
            with_vectors=False,
        )
        return results.points

    def get_cached_answer(self, question):
        vector = self.get_embedding(question)
        search_result = self.search_cache(vector)

        if search_result:
            for result in search_result:
                if result.score >= self.threshold:
                    return result.payload["response_text"]

        return None

    # def get_stats(self):
    #     return {
    #         "cache_hits": self.cache_client.count(collection_name=self.cache_collection_name).count,
    #         "cache_size": stats.vectors_count,
    #         "db_collection_name": self.db_collection_name
    #     }