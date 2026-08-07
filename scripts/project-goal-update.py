#!/usr/bin/env python3
"""project-goal-update：写入项目大目标（content_profile.goal）"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api, with_project_id


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    p = with_project_id(params)
    goal = params.get("goal")
    if not isinstance(goal, dict):
        raise ValueError("缺少 goal 对象")
    request_api(
        "POST",
        "/v1/project_goal/update",
        body={"project_id": p["project_id"], "goal": goal},
    )
    return {"projectId": p["project_id"], "ok": True}


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python project-goal-update.py \'{"projectId":123,"goal":{"title":"..."}}\'',
            file=sys.stderr,
        )
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
