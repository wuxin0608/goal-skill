#!/usr/bin/env python3
"""file-upsert：创建或更新项目资料（有 id 则 update，否则 create）"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api, with_project_id


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    p = with_project_id(params)
    file_id = p.get("id")
    name = str(p.get("name") or "").strip()
    content = p.get("content")
    if content is None:
        content = ""
    content = str(content)

    if file_id is not None and int(file_id) > 0:
        body = {
            "id": int(file_id),
            "project_id": p["project_id"],
            "name": name,
            "content": content,
        }
        payload = request_api("POST", "/v1/project_files/update", body=body)
        return {"action": "update", "id": int(file_id), "result": payload}

    file_name = str(p.get("file_name") or p.get("fileName") or name or "note.md").strip()
    if not name:
        name = file_name
    body = {
        "project_id": p["project_id"],
        "name": name,
        "file_name": file_name,
        "content": content,
    }
    payload = request_api("POST", "/v1/project_files/create", body=body)
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or {}
    return {"action": "create", "info": info, "result": payload}


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python file-upsert.py \'{"name":"项目背景","content":"...","file_name":"背景.md"}\'',
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
