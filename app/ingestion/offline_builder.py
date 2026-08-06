import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import vector_db
from app.config import init_global_settings

from llama_index.core import StorageContext, SimpleDirectoryReader, VectorStoreIndex


def run_file_upload():

    init_global_settings()

    knowledge_base = "./app/data_knowledge"

    if not os.path.exists(knowledge_base) or not os.listdir(knowledge_base):
        raise FileNotFoundError(
            f"❌ Ingestion Error: The directory '{knowledge_base}' is missing or empty. "
            "Please create it and add your Leadway markdown files before running!"
        )
    
    print(f"📖 Scanning and loading all markdown documents from: {knowledge_base}...")
    reader = SimpleDirectoryReader(
        input_dir=knowledge_base,
        required_exts=[".md"],
        recursive=False 
    )
    documents = reader.load_data()
    print(f"📚 Successfully loaded {len(documents)} distinct documentation pages/files.")

    vector_store = vector_db()

    storage_context = StorageContext.from_defaults(vector_store= vector_store)

    VectorStoreIndex.from_documents(documents, storage_context= storage_context, show_progress= True, insert_batch_size= 10)

    print("\n🎉 Success! Your Qdrant Cloud cluster is now fully populated with all Leadway documentation files.")

if __name__ == "__main__":
    run_file_upload()






