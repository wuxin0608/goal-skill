#!/usr/bin/env python3
"""project-list：列出当前用户可管理的项目"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List

from common import request_skill


def run(_params=None) -> Dict[str, Any]:
    payload = request_skill("/v1/ainote/skill/project/list", {})
    raw_list = payload.get("list") or payload.get("data", {}).get("list") or []
    projects: List[Dict[str, Any]] = []
    for item in raw_list:
        if not isinstance(item, dict):
            continue
        projects.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "desc": item.get("desc"),
                "isActive": bool(item.get("isActive")),
            }
        )
    return {"projects": projects}


def main() -> int:
    try:
        print(json.dumps(run(), ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
