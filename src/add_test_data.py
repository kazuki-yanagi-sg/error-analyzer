import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from vector_store import VectorStore

load_dotenv()

def add_test_case():
    print("Adding specific test case for 'Command not found'...")
    
    content = """
    エラー解決事例:
    エラー: zsh: command not found: yyy
    原因: 入力されたコマンド 'yyy' がシステムにインストールされていないか、パスが通っていません。
    解決策:
    1. コマンドのスペルを確認してください。
    2. そのツールがインストールされているか確認してください（例: brew list）。
    3. インストールされていない場合は、適切なパッケージマネージャー（brew, apt, pipなど）でインストールしてください。
    """
    
    doc = Document(page_content=content, metadata={"type": "manual_test_case"})
    
    vs = VectorStore()
    vs.add_documents([doc])
    print("Test case added successfully.")

if __name__ == "__main__":
    add_test_case()
