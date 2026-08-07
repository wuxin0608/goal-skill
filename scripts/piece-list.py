#!/usr/bin/env python3
"""piece-list：拉取全案任务成稿列表"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    task_id = params.get("taskId") or params.get("project_task_id") or params.get("id")
    if task_id is None:
        raise ValueError("缺少 taskId")
    task_id = int(task_id)
    if task_id <= 0:
        raise ValueError("taskId 必须大于 0")

    payload = request_api(
        "GET",
        "/v1/project_piece/list",
        params={"project_task_id": task_id},
    )
    raw = payload.get("list") or payload.get("data", {}).get("list") or []
    return {"taskId": task_id, "list": raw}


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print('用法: python piece-list.py \'{"taskId":123}\'', file=sys.stderr)
        return 1
    try:
        params = json.loads(argv[0])
        if not isinstance(params, dict):
            raise ValueError("参数必须是 JSON 对象")
        print(json.dumps(run(params), ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
