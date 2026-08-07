#!/usr/bin/env python3
"""content-task-claim：原子领取任务执行权，返回 batch_tag"""

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
    body: Dict[str, Any] = {
        "id": task_id,
        "trigger_source": str(params.get("trigger_source") or params.get("source") or "agent"),
    }
    payload = request_api("POST", "/v1/project_task/claim", body=body, timeout=60)
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or {}
    claimed = bool(info.get("claimed")) if isinstance(info, dict) else False
    out: Dict[str, Any] = {"taskId": task_id, "claimed": claimed, "info": info}
    if isinstance(info, dict):
        if info.get("batch_tag"):
            out["batch_tag"] = info["batch_tag"]
        if info.get("reason"):
            out["reason"] = info["reason"]
        task = info.get("task")
        if isinstance(task, dict):
            out["task"] = task
            out["expected_piece_count"] = task.get("expected_piece_count")
            out["topics"] = task.get("topics")
            out["content_type_config"] = task.get("content_type_config")
    return out


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print('用法: python content-task-claim.py \'{"taskId":123}\'', file=sys.stderr)
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
