#!/usr/bin/env python3
"""project-use：校验项目成员身份，并写入本地 .cache/project.json（服务端不存默认项目）"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_skill, save_project


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    project_id = params.get("projectId") or params.get("project_id")
    if project_id is None:
        raise ValueError("缺少 projectId")
    project_id = int(project_id)
    if project_id <= 0:
        raise ValueError("projectId 必须大于 0")

    payload = request_skill(
        "/v1/ainote/skill/project/use",
        {"projectId": project_id, "project_id": project_id},
    )
    data = payload.get("data") or {}
    info = data.get("info") or {}
    name = str(info.get("name") or "").strip()
    save_project(project_id, name)
    return {
        "projectId": project_id,
        "name": name,
        "cached": True,
        "result": data,
    }


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print('用法: python project-use.py \'{"projectId":123}\'', file=sys.stderr)
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
