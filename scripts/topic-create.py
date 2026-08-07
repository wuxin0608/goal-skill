#!/usr/bin/env python3
"""topic-create：创建选题"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api, with_project_id


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    p = with_project_id(params)
    title = str(p.get("title") or "").strip()
    if not title:
        raise ValueError("缺少 title")
    body = {
        "project_id": p["project_id"],
        "title": title,
        "angle": str(p.get("angle") or "").strip(),
        "audience": str(p.get("audience") or "").strip(),
    }
    payload = request_api("POST", "/v1/project_topics/create", body=body)
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or {}
    return {"info": info, "result": payload}


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python topic-create.py \'{"title":"选题标题","angle":"切入角度","audience":"受众"}\'',
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
