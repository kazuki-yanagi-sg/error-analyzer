import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

class AgentBase:
    def __init__(self, model_name="gpt-4o"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)

class Analyzer(AgentBase):
    def analyze(self, error_text):
        prompt = ChatPromptTemplate.from_template(
            """
            あなたは優秀なエンジニアです。以下のエラーメッセージを含むテキストを解析し、
            JSON形式で構造化されたデータを出力してください。
            
            抽出する項目:
            - language: プログラミング言語 (不明な場合は "unknown")
            - os: OS (不明な場合は "unknown")
            - error_type: エラーの種類または例外名
            - file_path: エラーが発生したファイルパス (あれば)
            - line_number: エラーが発生した行番号 (あれば)
            - error_message: 具体的なエラーメッセージ
            - stack_trace: スタックトレースの主要部分
            
            入力テキスト:
            {text}
            
            JSONのみを出力してください。Markdownのコードブロックは不要です。
            """
        )
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"text": error_text})

class Summarizer(AgentBase):
    def summarize(self, analysis_result):
        prompt = ChatPromptTemplate.from_template(
            """
            あなたは技術解説のプロです。以下の解析結果をもとに、
            1. エラーの技術的な原因
            2. ベクトルDB検索用のクエリ
            を作成してください。
            
            重要: 「検索クエリ」は、具体的な変数名やファイル名（例: 'git puad', 'app.py'）を含めず、
            エラーの本質的な意味（例: 'git command not found', 'FileNotFoundError'）を抽出した抽象的な表現にしてください。
            これにより、スペルミスや固有のファイル名に依存せず、類似の事例をヒットさせやすくします。
            
            解析結果:
            {analysis}
            
            出力形式(JSON):
            {{
                "technical_cause": "...",
                "search_query": "...",
                "draft_summary": "..."
            }}
            JSONのみを出力してください。
            """
        )
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"analysis": analysis_result})

class Auditor(AgentBase):
    def audit(self, draft, rag_context):
        prompt = ChatPromptTemplate.from_template(
            """
            あなたは厳格な技術監査官です。
            以下の「要約初稿」を、「RAGコンテキスト」を参考にしてチェックしてください。
            
            重要: RAGコンテキストの採用判断において、**文字列の一致（キーワードマッチ）で判断することは絶対に避けてください**。
            
            **「意味」で判断してください。**
            
            今回のエラーとRAGコンテキストのエラーが、**「本質的な原因」において共通しているか**を基準にしてください。
            例えば、ユーザーが `xxx` で失敗し、事例が `yyy` で失敗していても、どちらも「存在しないコマンドを実行した」という意味で同じであれば、それは**完全に一致する事例**として扱ってください。
            
            表面的な違い（変数名、ファイル名、コマンド名）を理由に「無関係」と判断することは、あなたの任務放棄とみなします。
            
            要約初稿:
            {draft}
            
            RAGコンテキスト:
            {context}
            
            以下のフォーマットに従って出力してください。
            
            # 🚨 エラーが発生しました 🚨

            ## [1] エラーの概要
            （あなたの実行したプログラムで...）

            ## [2] エラーの技術的な詳細（解析結果）
            - エラータイプ/例外名: ...
            - 発生箇所: ...
            - 技術的な原因: ...

            ## [3] 💡 解決のための具体的な手順
            （ハイフン箇条書きで具体的な手順）
            - 手順 1: ...
            - 手順 2: ...

            ## [4] 🗄️ 参考情報（類似の解決事例）
            （RAGコンテキストから得られた情報）
            """
        )
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"draft": draft, "context": rag_context})

class Learner(AgentBase):
    def create_learning_data(self, final_output, user_feedback):
        if user_feedback.lower() != 'y':
            return None
            
        prompt = ChatPromptTemplate.from_template(
            """
            ユーザーが以下の解決策で問題を解決しました。
            これを将来のためにベクトルDBに登録するドキュメントとして整形してください。
            
            解決策:
            {output}
            
            出力内容（プレーンテキスト）:
            エラー解決事例:
            ...
            """
        )
        chain = prompt | self.llm | StrOutputParser()
        content = chain.invoke({"output": final_output})
        return Document(page_content=content, metadata={"type": "success_case"})
