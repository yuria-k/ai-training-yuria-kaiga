from __future__ import annotations

import argparse
import logging
import sys
from typing import List
import os
from datetime import date

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage


def build_parser() -> argparse.ArgumentParser:
    """Day04のCLI引数を定義します（ユーザー入力テキスト）。"""
    p = argparse.ArgumentParser(prog="day04")
    p.add_argument("--text", required=True)
    return p


def _validate_args(args: argparse.Namespace) -> None:
    """引数の簡易バリデーションを行います（入力不備は exit code=2）。"""
    if not args.text:
        raise ValueError("--text is required")


def run_chain(text: str) -> str:
    load_dotenv()

    @tool
    def add(a: int, b: int) -> int:
        """2つの整数を足します"""
        if not isinstance(a, int):
            raise ValueError("a must be int")
        
        if not isinstance(b, int):
            raise ValueError("b must be int")

        logging.info(
            f"tool:add called a={a} b={b}"
        )
        return a + b

    region = os.getenv("AWS_REGION")

    model_id = os.getenv(
        "BEDROCK_MODEL_ID",
        "apac.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )

    if not region:
        raise RuntimeError("AWS_REGION is not set")

    llm = ChatBedrock(
        model_id=model_id,
        region_name=region,
    )

    llm_with_tools = llm.bind_tools([add])

    response = llm_with_tools.invoke(
        [HumanMessage(content=f"""ユーザーの質問です。 {text} 足し算が必要な場合はaddツールを使ってください。""")]
    )

    if response.tool_calls:

        tool_call = response.tool_calls[0]

        tool_result = add.invoke(
            tool_call["args"]
    )

        return f"計算結果は{tool_result}です。"

    return response.content


def main(argv: List[str] | None = None) -> int:
    """CLIのエントリポイントです。

    受講者は `run_chain()` の実装に集中し、ここは原則編集しません。
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        _validate_args(args)
    except Exception as e:
        logging.error(str(e))
        print(str(e), file=sys.stderr)
        return 2

    try:
        out = run_chain(args.text)
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
