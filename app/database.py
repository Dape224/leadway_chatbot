import os
import time
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from llama_index.vector_stores.qdrant import QdrantVectorStore

qdrant_key = os.getenv("QDRANT_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")

def vector_db() -> QdrantVectorStore:
    for att in range(3):
        try:
            active_client= QdrantClient(api_key= qdrant_key, url= qdrant_url, timeout= 1200, check_compatibility=False)

            collection_name = "leadway_insurance_documentation"
            if not active_client.collection_exists(collection_name= collection_name):
                active_client.create_collection(collection_name= collection_name, vectors_config= VectorParams(
                    size= 3072, distance= Distance.COSINE
                ))
            
            return QdrantVectorStore(collection_name= collection_name, client= active_client)

        except Exception as error:
            print(f"⚠️ Network check attempt {att + 1} failed. Retrying in 3 seconds... Error: {error}")
            time.sleep(3)
    raise ConnectionError(f"❌ Failed to reach Qdrant Cloud. Check your internet connection and .env URL format")
