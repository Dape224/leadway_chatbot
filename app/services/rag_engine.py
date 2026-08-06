import os
import sys
from llama_index.core import VectorStoreIndex

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.config import init_global_settings
from app.database import vector_db

def get_embedded_response():
    """
    Hooks into your existing populated Qdrant Cloud cluster,
    applies a strict system persona prompt, and returns a fast query engine.
    """
    init_global_settings()

    vector_store = vector_db()

    index = VectorStoreIndex.from_vector_store(vector_store= vector_store)

    query_engine = index.as_query_engine(
        similarity_top_k= 7)

    print("🎯 Advanced Sub-Question Query Router successfully initialized.")
    return query_engine

if __name__ == "__main__":
    engine = get_embedded_response()
    
    
    test_query = "What are the available health insurance plans?"
    print(f"\n❓ Sending Live Query: '{test_query}'")
    
   
    response = engine.query(test_query)
    
    print("\n🤖 Gemini Generated Response Output:", response)

