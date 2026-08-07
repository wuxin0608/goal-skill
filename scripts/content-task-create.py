#!/usr/bin/env python3
"""content-task-create：创建全案文案任务（skip_ai，仅落库）"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api, with_project_id

DEFAULT_CONTENT_TYPES = ["xiaohongshu"]


def _default_piece_count(type_id: str) -> int:
    return 10 if type_id == "private_chat" else 4


def _build_content_type_config(content_types: List[str], piece_counts: Optional[Dict[str, int]] = None) -> List[Dict[str, Any]]:
    piece_counts = piece_counts or {}
    cfg: List[Dict[str, Any]] = []
    for t in content_types:
        t = str(t).strip()
        if not t:
            continue
        pc = piece_counts.get(t)
        if pc is None:
            pc = _default_piece_count(t)
        cfg.append(
            {
                "type": t,
                "enabled": True,
                "piece_count": int(pc),
                "project_template_ids": [],
                "reference_dirs": [],
                "article_length": "1500",
                "tone": "consultant",
                "project_device_id": None,
            }
        )
    if not cfg:
        return _build_content_type_config(DEFAULT_CONTENT_TYPES, piece_counts)
    return cfg


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    p = with_project_id(params)
    goal = str(p.get("goal") or p.get("topic") or "").strip()
    if not goal:
        raise ValueError("缺少 goal（推广方向）")

    raw_types = p.get("content_types") or p.get("contentTypes") or DEFAULT_CONTENT_TYPES
    if isinstance(raw_types, str):
        content_types = [x.strip() for x in raw_types.split(",") if x.strip()]
    elif isinstance(raw_types, list):
        content_types = [str(x).strip() for x in raw_types if str(x).strip()]
    else:
        content_types = list(DEFAULT_CONTENT_TYPES)

    selected = p.get("selected_topics") or p.get("selectedTopics") or []
    if not isinstance(selected, list) or not selected:
        raise ValueError("缺少 selected_topics（用户已确认的选题）")

    body: Dict[str, Any] = {
        "project_id": p["project_id"],
        "brief": {
            "goal": goal,
            "topic": goal,
            "audience": str(p.get("audience") or "").strip(),
            "actionId": "agent",
            "actionLabel": "本地 Agent 写稿",
            "source": "agent",
        },
        "use_ai_topics": False,
        "skip_ai": True,
        "source": "agent",
        "selected_topics": selected,
        "content_type_config": p.get("content_type_config")
        or p.get("contentTypeConfig")
        or _build_content_type_config(content_types),
    }

    # 可选调度：manual / once / weekly
    for key in (
        "schedule_type",
        "scheduleType",
        "schedule_enabled",
        "scheduleEnabled",
        "schedule_config",
        "scheduleConfig",
    ):
        if p.get(key) is not None:
            # normalize below
            pass
    st = str(p.get("schedule_type") or p.get("scheduleType") or "manual").strip() or "manual"
    body["schedule_type"] = st
    if p.get("schedule_config") is not None or p.get("scheduleConfig") is not None:
        body["schedule_config"] = p.get("schedule_config") or p.get("scheduleConfig")
    if p.get("schedule_enabled") is not None or p.get("scheduleEnabled") is not None:
        body["schedule_enabled"] = bool(p.get("schedule_enabled") if p.get("schedule_enabled") is not None else p.get("scheduleEnabled"))

    payload = request_api("POST", "/v1/project_task/create", body=body, timeout=120)
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or {}
    task_id = info.get("id") if isinstance(info, dict) else None
    result: Dict[str, Any] = {"info": info, "result": payload}
    if task_id is not None:
        result["taskId"] = int(task_id)
    if isinstance(info, dict) and info.get("topics"):
        result["topics"] = info["topics"]
    return result


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python content-task-create.py \'{"goal":"推广方向","selected_topics":[{"title":"选题A"}]}\'',
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
