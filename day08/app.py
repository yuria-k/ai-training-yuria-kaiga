from __future__ import annotations

import argparse
import logging
import sys
from typing import List


def build_parser() -> argparse.ArgumentParser:
    """Day08のCLI引数を定義します（入力と上限設定）。"""
    p = argparse.ArgumentParser(prog="day08")
    p.add_argument("--text", required=True)
    p.add_argument("--max-steps", type=int, default=10)
    p.add_argument("--max-retry", type=int, default=1)
    return p


def _validate_args(args: argparse.Namespace) -> None:
    """引数の簡易バリデーションを行います（入力不備は exit code=2）。"""
    if not args.text:
        raise ValueError("--text is required")
    if not (1 <= args.max_steps <= 50):
        raise ValueError("--max-steps must be between 1 and 50")
    if not (0 <= args.max_retry <= 5):
        raise ValueError("--max-retry must be between 0 and 5")


def run_graph(*, text: str, max_steps: int, max_retry: int) -> str:
    """リトライ/フォールバック付きフロー"""

    step_count = 0
    retry_count = 0

    while True:
        step_count += 1

        if step_count > max_steps:
            raise RuntimeError(
                f"max_steps ({max_steps}) reached. Aborting to avoid infinite loop."
            )

        try:
            # ---------------------------------
            # 失敗ケースを意図的に再現
            # ---------------------------------
            if "不完全なJSON" in text:
                response = '{"answer": "テスト"'  # JSON破損
            else:
                response = '{"answer": "正常に処理できました"}'

            import json

            data = json.loads(response)

            return data["answer"]

        except Exception as e:
            logging.warning(
                "step=%s retry=%s parse failed: %s",
                step_count,
                retry_count,
                e,
            )

            retry_count += 1

            # -----------------------------
            # リトライ
            # -----------------------------
            if retry_count <= max_retry:
                logging.info(
                    "retrying... (%s/%s)",
                    retry_count,
                    max_retry,
                )

                # 再生成した想定
                text = text.replace("不完全なJSON", "")
                continue

            # -----------------------------
            # フォールバック
            # -----------------------------
            return (
                f"フォールバック応答: "
                f"最大リトライ回数({max_retry})に到達したため通常処理を中断しました。"
            )


def main(argv: List[str] | None = None) -> int:
    """CLIのエントリポイントです。

    受講者は `run_graph()` を実装します。ここは引数解析/検証/上限の適用/終了コードを担当します。
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)

    try:
        _validate_args(args)
    except Exception as e:
        logging.error(str(e))
        print(str(e), file=sys.stderr)
        return 2

    logging.info("max-steps=%s max-retry=%s", args.max_steps, args.max_retry)

    try:
        out = run_graph(text=args.text, max_steps=args.max_steps, max_retry=args.max_retry)
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
