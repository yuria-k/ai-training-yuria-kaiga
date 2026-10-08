from __future__ import annotations

import argparse
import logging
import sys
from typing import List


def build_parser() -> argparse.ArgumentParser:
    """Day05のCLI引数を定義します（質問文）。"""
    p = argparse.ArgumentParser(prog="day05")
    p.add_argument("--question", required=True)
    return p


def _validate_args(args: argparse.Namespace) -> None:
    """引数の簡易バリデーションを行います（入力不備は exit code=2）。"""
    if not args.question:
        raise ValueError("--question is required")


def answer_with_rag(question: str) -> str:
    from pathlib import Path

    data_dir = Path(__file__).parent / "data"

    if not data_dir.exists():
        raise FileNotFoundError("day05/data が存在しません")

    keyword = (
        question.replace("について教えて", "")
        .replace("とは", "")
        .strip()
    )

    sources = []

    for file in data_dir.glob("*.txt"):
        text = file.read_text(encoding="utf-8")

        if keyword.lower() in text.lower():
            excerpt = text[:100].replace("\n", " ")

            sources.append(
                f'- {file.name} (excerpt: "{excerpt}")'
            )

    if not sources:
        return (
            "Answer: 該当する根拠が見つかりません。\n\n"
            "Sources:\n"
            "- (none)"
        )

    answer = (
        sources[0]
        .split('excerpt: "')[1]
        .rstrip('")')
    )

    return (
        f"Answer: {answer}\n\n"
        "Sources:\n"
        + "\n".join(sources)
    )


def main(argv: List[str] | None = None) -> int:
    """CLIのエントリポイントです。

    受講者は `answer_with_rag()` を実装します。
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
        out = answer_with_rag(args.question)
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
