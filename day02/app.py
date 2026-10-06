from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import List, Optional

from dotenv import load_dotenv
import json

import boto3
from botocore.config import Config
from botocore.exceptions import (
    NoCredentialsError,
    ClientError,
    ConnectTimeoutError,
    ReadTimeoutError,
)


def build_parser() -> argparse.ArgumentParser:
    """Day02のCLI引数を定義します（READMEの機能要件に対応）。"""
    p = argparse.ArgumentParser(prog="day02")
    p.add_argument("--prompt", required=True)
    p.add_argument("--region", default=None)
    p.add_argument("--model-id", default=None)
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--max-tokens", type=int, default=512)
    p.add_argument("--timeout-sec", type=int, default=30)
    return p


def _validate_args(args: argparse.Namespace) -> None:
    """引数の簡易バリデーションを行います（入力不備は exit code=2）。"""
    if not args.prompt:
        raise ValueError("--prompt is required")
    if not (0.0 <= args.temperature <= 1.0):
        raise ValueError("--temperature must be between 0.0 and 1.0")
    if args.max_tokens <= 0:
        raise ValueError("--max-tokens must be a positive integer")
    if args.timeout_sec <= 0:
        raise ValueError("--timeout-sec must be a positive integer")


def invoke_bedrock(
    *,
    prompt: str,
    region: str,
    model_id: str,
    temperature: float,
    max_tokens: int,
    timeout_sec: int,
) -> str:
    """Bedrockを呼び出して回答本文（文字列）を返します。"""

    try:
        config = Config(
            connect_timeout=timeout_sec,
            read_timeout=timeout_sec,
            retries={"max_attempts": 1},
        )

        client = boto3.client(
            "bedrock-runtime",
            region_name=region,
            config=config,
        )

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
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

        return response_body["content"][0]["text"]

    except NoCredentialsError as e:
        raise RuntimeError(
            "AWS認証情報が見つかりません。AWS_PROFILEや credentials を確認してください。"
        ) from e

    except (ConnectTimeoutError, ReadTimeoutError) as e:
        raise RuntimeError(
            f"Bedrock接続がタイムアウトしました。timeout-sec={timeout_sec} を確認してください。"
        ) from e

    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        if error_code in (
            "AccessDeniedException",
            "UnauthorizedOperation",
        ):
            raise RuntimeError(
                f"AWS権限エラーです。IAM権限を確認してください。({error_code})"
            ) from e

        raise RuntimeError(
            f"AWSエラーが発生しました。({error_code}){e}"
        ) from e


def main(argv: List[str] | None = None) -> int:
    """CLIのエントリポイントです。

    受講者は原則 `invoke_bedrock()` のみ実装し、それ以外は触らない想定です。
    """
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        _validate_args(args)
    except Exception as e:
        logging.error(str(e))
        print(str(e), file=sys.stderr)
        return 2

    region: Optional[str] = args.region or os.getenv("AWS_REGION")
    model_id: Optional[str] = args.model_id or os.getenv("BEDROCK_MODEL_ID")

    if not region:
        msg = "region is required: set --region or AWS_REGION"
        logging.error(msg)
        print(msg, file=sys.stderr)
        return 2

    if not model_id:
        msg = "model-id is required: set --model-id or BEDROCK_MODEL_ID"
        logging.error(msg)
        print(msg, file=sys.stderr)
        return 2

    logging.info(
        "region=%s model-id=%s temperature=%s max-tokens=%s timeout-sec=%s",
        region,
        model_id,
        args.temperature,
        args.max_tokens,
        args.timeout_sec,
    )

    try:
        reply = invoke_bedrock(
            prompt=args.prompt,
            region=region,
            model_id=model_id,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            timeout_sec=args.timeout_sec,
        )
        print(reply)
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
