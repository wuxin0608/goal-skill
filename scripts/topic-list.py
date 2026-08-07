#!/usr/bin/env python3
"""topic-list：列出当前项目选题库"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict

from common import request_api, with_project_id


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    p = with_project_id(params)
    payload = request_api(
        "GET",
        "/v1/project_topics/list",
        params={"project_id": p["project_id"]},
    )
    raw = payload.get("list") or payload.get("data", {}).get("list") or []
    return {"projectId": p["project_id"], "list": raw}


def main() -> int:
    argv = list(sys.argv[1:])
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
