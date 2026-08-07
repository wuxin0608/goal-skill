#!/usr/bin/env python3
"""piece-create：保存 Agent 已写好的成稿（仅落库，不触发后端模型）"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api, with_project_id


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    p = with_project_id(params)
    result = str(p.get("result") or "").strip()
    if not result:
        raise ValueError("缺少 result（成稿正文）")

    title = str(p.get("title") or p.get("goal") or "").strip()
    if not title:
        first = result.splitlines()[0].strip() if result else ""
        title = first[:40] if first else "Agent 成稿"

    body: Dict[str, Any] = {
        "project_id": p["project_id"],
        "title": title,
        "result": result,
        "content_type": str(p.get("content_type") or p.get("contentType") or "xiaohongshu").strip()
        or "xiaohongshu",
    }
    for src, dst in (
        ("angle", "angle"),
        ("audience", "audience"),
        ("project_task_id", "project_task_id"),
        ("taskId", "project_task_id"),
        ("project_task_topic_id", "project_task_topic_id"),
        ("projectTaskTopicId", "project_task_topic_id"),
        ("topicId", "project_task_topic_id"),
        ("project_device_id", "project_device_id"),
        ("projectDeviceId", "project_device_id"),
        ("project_template_id", "project_template_id"),
        ("projectTemplateId", "project_template_id"),
        ("batch_tag", "batch_tag"),
        ("batchTag", "batch_tag"),
        ("batch_piece_index", "batch_piece_index"),
        ("batchPieceIndex", "batch_piece_index"),
    ):
        if p.get(src) is not None and dst not in body:
            body[dst] = p[src]

    payload = request_api("POST", "/v1/project_piece/create", body=body, timeout=60)
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or {}
    out: Dict[str, Any] = {"info": info, "result": payload}
    if isinstance(info, dict):
        if info.get("id") is not None:
            out["pieceId"] = int(info["id"])
        if info.get("project_task_id") is not None:
            out["taskId"] = int(info["project_task_id"])
        if info.get("batch_tag"):
            out["batch_tag"] = info["batch_tag"]
        if info.get("idempotent"):
            out["idempotent"] = True
    return out


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python piece-create.py \'{"taskId":1,"topicId":2,"result":"成稿","batch_tag":"x","batch_piece_index":1}\'',
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
