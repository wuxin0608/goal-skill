#!/usr/bin/env python3
"""add-template：导入笔记模板（与 v1/xhs/template/add 一致，仅 keyword）"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from common import request_skill


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    keyword = str(params.get("keyword") or "").strip()
    if not keyword:
        raise ValueError("缺少 keyword")

    payload = request_skill("/v1/ainote/skill/add/template", {"keyword": keyword})
    raw_list = payload.get("list") or payload.get("data", {}).get("list") or []
    return {"templateResult": {"list": raw_list, "code": payload.get("code", 20000)}}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add xhs template via ainote skill API.")
    parser.add_argument("--params", default=None, help="JSON 参数对象")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.params:
        print(
            '用法: python add-template.py --params \'{"keyword":"https://www.xiaohongshu.com/explore/..."}\'',
            file=sys.stderr,
        )
        return 1
    try:
        params = json.loads(args.params)
        if not isinstance(params, dict):
            raise ValueError("--params 必须是 JSON 对象")
        result = run(params)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
