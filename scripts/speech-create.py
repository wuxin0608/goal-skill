#!/usr/bin/env python3
"""speech-create：创建话术（title + copies），写入 project_speech"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api, with_project_id


def _ensure_group_id(project_id: int, preferred: Optional[int] = None) -> int:
    if preferred and int(preferred) > 0:
        return int(preferred)
    payload = request_api("GET", "/v1/project_speech_groups/list", params={"project_id": project_id})
    data = payload.get("data") or payload
    groups = data.get("list") or payload.get("list") or []
    if not isinstance(groups, list):
        groups = []
    for g in groups:
        if isinstance(g, dict) and str(g.get("title") or "").strip() == "默认话术":
            return int(g["id"])
    if groups and isinstance(groups[0], dict) and groups[0].get("id") is not None:
        return int(groups[0]["id"])
    created = request_api(
        "POST",
        "/v1/project_speech_groups/create",
        body={"project_id": project_id, "title": "默认话术", "sort_order": 0},
    )
    info = created.get("info") or created.get("data", {}).get("info") or created.get("data") or {}
    gid = info.get("id") if isinstance(info, dict) else None
    if not gid:
        raise ValueError("无法创建默认话术分组")
    return int(gid)


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    p = with_project_id(params)
    copies_raw = p.get("copies")
    copies: List[str] = []
    if isinstance(copies_raw, list):
        copies = [str(c).strip() for c in copies_raw if str(c).strip()]
    elif isinstance(copies_raw, str) and copies_raw.strip():
        copies = [copies_raw.strip()]
    single = str(p.get("content") or p.get("text") or p.get("copy") or "").strip()
    if single and single not in copies:
        copies.append(single)
    if not copies:
        raise ValueError("缺少 copies（至少一条话术文案）")

    title = str(p.get("title") or "").strip()
    if not title:
        title = copies[0][:40]

    group_id = _ensure_group_id(
        int(p["project_id"]),
        preferred=p.get("project_speech_group_id") or p.get("groupId") or p.get("group_id"),
    )
    body: Dict[str, Any] = {
        "project_id": p["project_id"],
        "project_speech_group_id": group_id,
        "title": title,
        "copies": copies,
    }
    if p.get("sort_order") is not None:
        body["sort_order"] = p["sort_order"]

    payload = request_api("POST", "/v1/project_speech/create", body=body)
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or {}
    out: Dict[str, Any] = {"info": info, "result": payload, "groupId": group_id}
    if isinstance(info, dict) and info.get("id") is not None:
        out["speechId"] = int(info["id"])
    return out


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python speech-create.py \'{"title":"开口破冰","copies":["你好呀","最近在忙什么"]}\'',
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
