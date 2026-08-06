import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.mistralai import MistralAI

load_dotenv()
llm_key = os.getenv("MISTRAL_API_KEY")
if not llm_key:
        raise ValueError("❌ Production Error: GEMINI_API_KEY is missing from environment variables!")
gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
        raise ValueError("❌ Production Error: GEMINI_API_KEY is missing from environment variables!")

http_opts = {"api_version": "v1alpha"} 
embed_config = {"output_dimensionality": 3072}

def init_global_settings():
    Settings.llm = MistralAI(model = "mistral-medium-2505", api_key= llm_key, temperature= 0.2)
    Settings.embed_model = GoogleGenAIEmbedding(
    model_name="gemini-embedding-2-preview",  
    api_key=gemini_key,
    http_options=http_opts,
    embedding_config=embed_config
)