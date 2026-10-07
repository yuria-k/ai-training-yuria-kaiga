from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any, Dict, List
import os

from dotenv import load_dotenv

import boto3
from botocore.config import Config
from botocore.exceptions import (
    NoCredentialsError,
    ClientError,
    ConnectTimeoutError,
    ReadTimeoutError,
)


def build_parser() -> argparse.ArgumentParser:
    """Day03のCLI引数を定義します（要件文とリトライ回数）。"""
    p = argparse.ArgumentParser(prog="day03")
    p.add_argument("--requirements", required=True)
    p.add_argument("--max-retry", type=int, default=1)
    return p


def _validate_args(args: argparse.Namespace) -> None:
    """引数の簡易バリデーションを行います（入力不備は exit code=2）。"""
    if not args.requirements:
        raise ValueError("--requirements is required")
    if not (0 <= args.max_retry <= 3):
        raise ValueError("--max-retry must be between 0 and 3")


def generate_json(requirements: str) -> str:
    region = os.getenv("AWS_REGION")

    model_id = os.getenv(
        "BEDROCK_MODEL_ID",
        "apac.anthropic.claude-3-5-sonnet-20241022-v2:0"
    )

    if not region:
        raise RuntimeError(
            "AWS_REGION is not set"
        )

    prompt = f"""
あなたはシステム分析アシスタントです。

以下の要件を分析してください。

要件:
{requirements}

次のJSON形式のみ出力してください。

{{
  "title": "要件のタイトル",
  "tasks": [
    {{
      "id": 1,
      "description": "作業内容",
      "acceptance_criteria": "完了条件"
    }}
  ],
  "risks": [
    "リスク"
  ]
}}

ルール:
- JSON以外を出力しない
- markdownを使わない
- 説明文を書かない
- title を必ず含める
- tasks を必ず含める
- risks を必ず含める
"""

    try:
        config = Config(
            connect_timeout=30,
            read_timeout=30,
            retries={"max_attempts": 1},
        )

        client = boto3.client(
            "bedrock-runtime",
            region_name=region,
            config=config,
        )

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body),
        )

        response_body = json.loads(
            response["body"].read().decode("utf-8")
        )

        return response_body["content"][0]["text"].strip()

    except NoCredentialsError as e:
        raise RuntimeError(
            "AWS認証情報が見つかりません"
        ) from e

    except (
        ConnectTimeoutError,
        ReadTimeoutError,
    ) as e:
        raise RuntimeError(
            "Bedrock接続タイムアウト"
        ) from e

    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        raise RuntimeError(
            f"AWSエラー ({error_code})"
        ) from e


def validate_json(text: str) -> Dict[str, Any]:
    """生成結果のJSONを検証します（必須キーと型）。"""
    obj = json.loads(text)
    for key in ("title", "tasks", "risks"):
        if key not in obj:
            raise ValueError(f"missing key: {key}")
    if not isinstance(obj.get("tasks"), list):
        raise ValueError("tasks must be a list")
    return obj


def main(argv: List[str] | None = None) -> int:
    load_dotenv()

    """CLIのエントリポイントです。

    JSON生成→検証→（失敗時は再生成）までを制御します。受講者は `generate_json()` を実装します。
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

    last_err: Exception | None = None
    for _ in range(args.max_retry + 1):
        try:
            text = generate_json(args.requirements)
            validate_json(text)
            print(text)
            return 0
        except NotImplementedError as e:
            logging.error(str(e))
            print(str(e), file=sys.stderr)
            return 1
        except Exception as e:
            last_err = e

    msg = str(last_err) if last_err else "validation failed"
    logging.error(msg)
    print(msg, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
