import os
import time
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

class VectorStore:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.env = os.getenv("PINECONE_ENV")
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        
        if not self.api_key or not self.index_name:
            raise ValueError("PINECONE_API_KEY and PINECONE_INDEX_NAME must be set")

        self.pc = Pinecone(api_key=self.api_key)
        # Match the index dimension (1024) as per user's existing index
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1024)
        
        # Check if index exists, if not create it (optional, but good for setup)
        # For now, we assume it exists or we handle it gracefully
        existing_indexes = [i.name for i in self.pc.list_indexes()]
        if self.index_name not in existing_indexes:
             # Create index if not exists (Serverless spec for example)
             # Note: This might fail if the user is on a free tier and already has an index
             try:
                 self.pc.create_index(
                    name=self.index_name,
                    dimension=1024, # Match the embedding dimension
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                 while not self.pc.describe_index(self.index_name).status['ready']:
                     time.sleep(1)
             except Exception as e:
                 print(f"Warning: Could not create index {self.index_name}. It might already exist or permission denied. Error: {e}")

        self.index = self.pc.Index(self.index_name)
        self.vector_store = PineconeVectorStore(index=self.index, embedding=self.embeddings)

    def add_documents(self, documents):
        """
        Add documents to the vector store.
        documents: List of Document objects (LangChain)
        """
        return self.vector_store.add_documents(documents)

    def similarity_search(self, query, k=3):
        """
        Search for similar documents.
        """
        return self.vector_store.similarity_search(query, k=k)
