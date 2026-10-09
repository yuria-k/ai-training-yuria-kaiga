from __future__ import annotations

import argparse
import logging
import sys
from typing import List


def build_parser() -> argparse.ArgumentParser:
    """Day07のCLI引数を定義します（入力と分類モード）。"""
    p = argparse.ArgumentParser(prog="day07")
    p.add_argument("--text", required=True)
    p.add_argument("--mode", choices=["llm", "rule"], default="rule")
    return p


def _validate_args(args: argparse.Namespace) -> None:
    """引数の簡易バリデーションを行います（入力不備は exit code=2）。"""
    if not args.text:
        raise ValueError("--text is required")


def run_graph(*, text: str, mode: str) -> str:
    from langgraph.graph import StateGraph, END

    # ------------------
    # 分類ノード
    # ------------------
    def classify_node(state):

        user_text = state["input"]

        if mode == "rule":

            if "要約" in user_text:
                state["intent"] = "summarize"

            elif "手順" in user_text or "実装" in user_text:
                state["intent"] = "plan"

            elif "教えて" in user_text or "調べて" in user_text:
                state["intent"] = "rag"

            else:
                state["intent"] = "default"

        else:
            # 簡易LLMモード（仮）
            if "要約" in user_text:
                state["intent"] = "summarize"

            elif "手順" in user_text or "実装" in user_text:
                state["intent"] = "plan"

            elif "教えて" in user_text or "調べて" in user_text:
                state["intent"] = "rag"

            else:
                state["intent"] = "default"

        logging.info("classified intent=%s", state["intent"])

        return state

    # ------------------
    # RAGノード
    # ------------------
    def rag_node(state):

        logging.info("route -> rag")

        state["output"] = (
            f"【RAG処理】\n"
            f"'{state['input']}' に対する情報を検索しました。"
        )

        return state

    # ------------------
    # 要約ノード
    # ------------------
    def summarize_node(state):

        logging.info("route -> summarize")

        state["output"] = (
            f"【要約処理】\n"
            f"'{state['input']}' を要約しました。"
        )

        return state

    # ------------------
    # タスク分解ノード
    # ------------------
    def plan_node(state):

        logging.info("route -> plan")

        state["output"] = (
            "【タスク分解】\n"
            "1. 要件確認\n"
            "2. 設計\n"
            "3. 実装\n"
            "4. テスト"
        )

        return state

    # ------------------
    # フォールバック
    # ------------------
    def default_node(state):

        logging.info("route -> default")

        state["output"] = (
            "分類できませんでした。"
            "別の表現で入力してください。"
        )

        return state

    # ------------------
    # ルーティング
    # ------------------
    def route(state):
        return state["intent"]

    logging.info("before StateGraph")

    workflow = StateGraph(dict)

    logging.info("after StateGraph")

    workflow.add_node("classify", classify_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("plan", plan_node)
    workflow.add_node("default", default_node)

    workflow.set_entry_point("classify")

    workflow.add_conditional_edges(
        "classify",
        route,
        {
            "rag": "rag",
            "summarize": "summarize",
            "plan": "plan",
            "default": "default",
        },
    )

    workflow.add_edge("rag", END)
    workflow.add_edge("summarize", END)
    workflow.add_edge("plan", END)
    workflow.add_edge("default", END)

    app = workflow.compile()

    result = app.invoke(
        {
            "input": text,
            "intent": "",
            "output": "",
            "errors": "",
        }
    )

    return result["output"]


def main(argv: List[str] | None = None) -> int:
    """CLIのエントリポイントです。

    受講者は `run_graph()` を実装します。ここは引数解析/検証/終了コードを担当します。
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)

    try:
        _validate_args(args)
    except Exception as e:
        logging.error(str(e))
        print(str(e), file=sys.stderr)
        return 2

    logging.info("mode=%s", args.mode)

    try:
        out = run_graph(text=args.text, mode=args.mode)
        print(out)
        return 0
    except NotImplementedError as e:
        logging.error(str(e))
        print(str(e), file=sys.stderr)
        return 1
    except Exception as e:
        logging.error("%s", e)
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
