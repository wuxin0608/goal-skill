#!/usr/bin/env python3
"""content-task-list：列出项目下内容任务（只读）"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api, with_project_id


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    p = with_project_id(params)
    status = str(p.get("status") or "all").strip() or "all"
    q: Dict[str, Any] = {"project_id": p["project_id"]}
    if status and status != "all":
        q["status"] = status
    payload = request_api("GET", "/v1/project_task/list", params=q)
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    lst = payload.get("list") or data.get("list") or []
    stats = payload.get("stats") or data.get("stats") or {}
    return {
        "projectId": p["project_id"],
        "count": len(lst) if isinstance(lst, list) else 0,
        "list": lst,
        "stats": stats,
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
