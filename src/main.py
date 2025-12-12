import sys
import json
import os
from dotenv import load_dotenv
from agents import Analyzer, Summarizer, Auditor, Learner
from vector_store import VectorStore

# Load environment variables
load_dotenv()

def read_input():
    # Check if input is piped
    if not sys.stdin.isatty():
        return sys.stdin.read()
    # Check if file argument is provided
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            return f.read()
    print("Usage: python src/main.py < error.txt OR cat error.txt | python src/main.py")
    sys.exit(1)

def main():
    error_text = read_input()
    if not error_text:
        print("Error: No input provided.")
        sys.exit(1)

    print("Analyzing error...", file=sys.stderr)
    
    # Initialize agents
    analyzer = Analyzer()
    summarizer = Summarizer()
    auditor = Auditor()
    learner = Learner()
    vector_store = VectorStore()

    # 1. Analyze
    try:
        analysis_json = analyzer.analyze(error_text)
        # Ensure it's valid JSON (sometimes LLM adds extra text)
        if "```json" in analysis_json:
            analysis_json = analysis_json.split("```json")[1].split("```")[0]
        elif "```" in analysis_json:
            analysis_json = analysis_json.split("```")[1].split("```")[0]
        analysis_data = json.loads(analysis_json)
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        # Fallback or exit
        sys.exit(1)

    # 2. Summarize & Query Generation
    try:
        summary_json = summarizer.summarize(analysis_json)
        if "```json" in summary_json:
            summary_json = summary_json.split("```json")[1].split("```")[0]
        elif "```" in summary_json:
            summary_json = summary_json.split("```")[1].split("```")[0]
        summary_data = json.loads(summary_json)
    except Exception as e:
        print(f"Error during summarization: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. RAG Search
    query = summary_data.get("search_query", analysis_data.get("error_message", ""))
    rag_docs = vector_store.similarity_search(query)
    rag_context = "\n\n".join([d.page_content for d in rag_docs])

    # 4. Audit & Final Output
    final_output = auditor.audit(summary_json, rag_context)
    print(final_output)

    # 5. Feedback Loop
    print("\n" + "="*50)
    print("【自己学習フィードバック】")
    try:
        # If stdin is not a TTY and we've already read from it, input() might fail or return EOF immediately
        if not sys.stdin.isatty():
             # If we read from stdin (piped), we can't easily get user input for feedback unless we reopen tty
             # For now, we just skip feedback in non-interactive mode
             print("非対話モードのため、フィードバック入力をスキップします。", file=sys.stderr)
             return

        feedback = input("提案された手順でエラーは解決しましたか？ [Y/N] を入力してください: ").strip()

        if feedback.upper() == 'Y':
            print("フィードバックありがとうございます。解決事例として学習します...", file=sys.stderr)
            learning_doc = learner.create_learning_data(final_output, 'Y')
            if learning_doc:
                vector_store.add_documents([learning_doc])
                print("学習完了しました。", file=sys.stderr)
        else:
            print("フィードバックありがとうございます。", file=sys.stderr)
    except (EOFError, KeyboardInterrupt):
        print("\nフィードバック入力がキャンセルされました。", file=sys.stderr)

if __name__ == "__main__":
    main()
