#!/usr/bin/env python3
"""template-upsert：写入 project_templates；或 keyword/URL 走 skill add/template 导入"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api, request_skill, with_project_id


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    p = with_project_id(params)
    keyword = str(p.get("keyword") or "").strip()
    url = str(p.get("url") or "").strip()
    import_kw = keyword or url
    # 链接/关键词导入（小红书等）
    if import_kw and (import_kw.startswith("http") or p.get("import") is True or keyword):
        if not import_kw:
            raise ValueError("缺少 keyword/url")
        payload = request_skill(
            "/v1/ainote/skill/add/template",
            with_project_id({"keyword": import_kw, **{k: v for k, v in p.items() if k not in ("keyword", "url")}}),
        )
        raw_list = payload.get("list") or payload.get("data", {}).get("list") or []
        return {"action": "import", "list": raw_list, "result": payload}

    title = str(p.get("title") or p.get("name") or "").strip()
    if not title:
        raise ValueError("缺少 title/name（结构化创建）或 keyword/url（链接导入）")
    body: Dict[str, Any] = {
        "project_id": p["project_id"],
        "title": title,
        "name": str(p.get("name") or title).strip(),
    }
    for key in ("desc", "content_type", "prompt", "structure", "imgs", "original_id", "tags"):
        if p.get(key) is not None:
            body[key] = p[key]
    if p.get("contentType") is not None:
        body["content_type"] = p["contentType"]
    payload = request_api("POST", "/v1/project_templates/create", body=body, timeout=60)
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or {}
    tid = info.get("id") if isinstance(info, dict) else None
    return {"id": tid, "info": info, "result": payload, "action": "create"}


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python template-upsert.py \'{"projectId":1,"title":"对标A","content_type":"xiaohongshu"}\' '
            '或 \'{"projectId":1,"keyword":"https://www.xiaohongshu.com/explore/..."}\'',
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
