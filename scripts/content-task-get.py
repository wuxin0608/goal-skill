#!/usr/bin/env python3
"""content-task-get：查询全案任务详情与状态"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    task_id = params.get("taskId") or params.get("id") or params.get("project_task_id")
    if task_id is None:
        raise ValueError("缺少 taskId")
    task_id = int(task_id)
    if task_id <= 0:
        raise ValueError("taskId 必须大于 0")

    payload = request_api("GET", "/v1/project_task/get", params={"id": task_id})
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or {}
    status = info.get("status") if isinstance(info, dict) else None
    return {"taskId": task_id, "status": status, "info": info}


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print('用法: python content-task-get.py \'{"taskId":123}\'', file=sys.stderr)
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
