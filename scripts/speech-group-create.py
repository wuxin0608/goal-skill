#!/usr/bin/env python3
"""speech-group-create：创建话术分组"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, Optional

from common import request_api, with_project_id


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    p = with_project_id(params)
    title = str(p.get("title") or p.get("name") or "").strip()
    if not title:
        raise ValueError("缺少 title（话术分组名）")
    body: Dict[str, Any] = {
        "project_id": p["project_id"],
        "title": title,
        "sort_order": int(p.get("sort_order") or p.get("sortOrder") or 0),
    }
    payload = request_api("POST", "/v1/project_speech_groups/create", body=body)
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or {}
    out: Dict[str, Any] = {"info": info, "result": payload}
    if isinstance(info, dict) and info.get("id") is not None:
        out["groupId"] = int(info["id"])
    return out


def main(argv: Optional[list] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print('用法: python speech-group-create.py \'{"title":"开场破冰","sort_order":1}\'', file=sys.stderr)
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
