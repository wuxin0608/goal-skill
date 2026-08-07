#!/usr/bin/env python3
"""goal-diverge-trigger：创建 diverge_run，返回 runId 供本地发散后 finish"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api, with_project_id


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    p = with_project_id(params)
    goal_id = params.get("goalId") or params.get("goal_id")
    if goal_id is None:
        raise ValueError("缺少 goalId")
    goal_id = int(goal_id)
    if goal_id <= 0:
        raise ValueError("goalId 必须大于 0")
    body: Dict[str, Any] = {
        "project_id": p["project_id"],
        "goal_id": goal_id,
        "trigger": params.get("trigger") or "manual",
    }
    for key in ("brief", "template_id", "templateId"):
        if params.get(key) is not None:
            dst = "template_id" if key.lower().endswith("id") else key
            body[dst] = params[key]
    payload = request_api("POST", "/v1/project_task/diverge/trigger", body=body, timeout=60)
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or {}
    run_id = 0
    if isinstance(info, dict):
        run_id = int(info.get("id") or 0)
    return {"projectId": p["project_id"], "runId": run_id, "info": info}


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        params: Dict[str, Any] = {}
        if argv:
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
