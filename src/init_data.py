import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from vector_store import VectorStore

load_dotenv()

def generate_initial_data():
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    
    print("Generating initial data using LLM...")
    
    # Generate common Python/Docker errors and solutions
    prompt = """
    PythonやDockerの開発環境でよく発生するエラーと、その解決策を5つ挙げてください。
    それぞれを以下の形式で記述してください。
    
    エラー解決事例:
    エラー: [エラーメッセージ]
    原因: [原因]
    解決策: [解決手順]
    """
    
    response = llm.invoke(prompt)
    content = response.content
    
    # Split into documents (simple split by "エラー解決事例:")
    cases = content.split("エラー解決事例:")
    documents = []
    for case in cases:
        if case.strip():
            doc = Document(page_content="エラー解決事例:" + case.strip(), metadata={"type": "initial_data"})
            documents.append(doc)
            
    print(f"Generated {len(documents)} documents.")
    
    # Add to VectorStore
    vs = VectorStore()
    vs.add_documents(documents)
    print("Added documents to VectorStore.")

if __name__ == "__main__":
    generate_initial_data()
