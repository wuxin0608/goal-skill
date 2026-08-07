#!/usr/bin/env python3
"""task-list：获取笔记任务列表"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List

from common import request_skill, resolve_publish_key


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    publish_key = resolve_publish_key(params)
    category = str(params.get("category") or "published").strip()
    body = {
        "publishKey": publish_key,
        "category": category,
    }
    payload = request_skill("/v1/ainote/skill/task/list", body)
    raw_list = payload.get("list") or payload.get("data", {}).get("list") or []

    page_size = params.get("pageSize")
    page_num = params.get("pageNum")
    if page_size is not None and page_num is not None:
        size = int(page_size)
        num = int(page_num)
        if size <= 0 or num <= 0:
            raise ValueError("pageSize 与 pageNum 必须大于 0")
        start = (num - 1) * size
        end = start + size
        raw_list = raw_list[start:end]

    return {"noteshareListResult": {"list": raw_list, "code": payload.get("code", 20000)}}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch note task list via ainote skill API.")
    parser.add_argument(
        "--params",
        default=None,
        help='JSON 参数，例如 {"category":"published","deviceName":"设备1","pageSize":10,"pageNum":1}',
    )
    parser.add_argument("--category", default="published")
    parser.add_argument("--device-name", dest="deviceName", default=None)
    parser.add_argument("--page-size", type=int, default=None)
    parser.add_argument("--page-num", type=int, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.params:
            params = json.loads(args.params)
            if not isinstance(params, dict):
                raise ValueError("--params 必须是 JSON 对象")
        else:
            params = {"category": args.category}
            if args.deviceName:
                params["deviceName"] = args.deviceName
            if args.page_size is not None:
                params["pageSize"] = args.page_size
            if args.page_num is not None:
                params["pageNum"] = args.page_num

        result = run(params)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
