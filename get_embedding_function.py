from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.embeddings.bedrock import BedrockEmbeddings

def get_embedding_function():
    # # uses AWS Bedrock
    # embeddings = BedrockEmbeddings(
    #     credentials_profile_name="default", region_name="us-east-1"
    # )

    # uses Ollama local embeddings - requires Ollama to be running
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings
