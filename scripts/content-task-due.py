#!/usr/bin/env python3
"""content-task-due：列出到期/待立即执行的内容任务（Skill 主入口）"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api, with_project_id


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    # projectId 可选：省略则返回当前用户有权限的全部到期任务
    q: Dict[str, Any] = {}
    if params.get("projectId") is not None or params.get("project_id") is not None:
        p = with_project_id(params)
        q["project_id"] = p["project_id"]
    payload = request_api("GET", "/v1/project_task/due", params=q)
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    lst = payload.get("list") or data.get("list") or []
    return {
        "count": len(lst) if isinstance(lst, list) else 0,
        "list": lst,
        "hint": "对每个任务：content-task-claim → 本地写稿 piece-create → content-task-finish",
    }


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        params = json.loads(argv[0]) if argv else {}
        if not isinstance(params, dict):
            raise ValueError("参数必须是 JSON 对象")
        print(json.dumps(run(params), ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
