#!/usr/bin/env python3
"""content-task-create：创建任务（扁平 output_type；piece_* 可带选题）"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api, with_project_id

DEFAULT_KIND = "piece_xiaohongshu"


def _default_piece_count(type_id: str) -> int:
    return 10 if type_id == "private_chat" else 4


def _piece_content_type(kind: str) -> str:
    if kind.startswith("piece_"):
        return kind[len("piece_") :]
    return ""


def _build_content_type_config(content_type: str, piece_count: int) -> List[Dict[str, Any]]:
    return [
        {
            "type": content_type,
            "enabled": True,
            "piece_count": int(piece_count),
            "project_template_ids": [],
            "reference_dirs": [],
            "article_length": "1500",
            "tone": "consultant",
            "project_device_id": None,
        }
    ]


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    p = with_project_id(params)
    goal = str(p.get("goal") or p.get("topic") or p.get("prompt") or "").strip()
    if not goal:
        raise ValueError("缺少 goal / prompt（任务说明）")

    kind = str(p.get("output_type") or p.get("outputType") or "").strip()
    if not kind:
        raw_types = p.get("content_types") or p.get("contentTypes") or ["xiaohongshu"]
        if isinstance(raw_types, str):
            first = raw_types.split(",")[0].strip()
        elif isinstance(raw_types, list) and raw_types:
            first = str(raw_types[0]).strip()
        else:
            first = "xiaohongshu"
        kind = f"piece_{first}" if first and not first.startswith("piece_") else (first or DEFAULT_KIND)

    quantity = int(p.get("quantity") or 0)
    ct = _piece_content_type(kind)
    if quantity <= 0 and ct:
        quantity = _default_piece_count(ct)
    if quantity <= 0:
        quantity = 1

    selected = p.get("selected_topics") or p.get("selectedTopics") or []
    if not isinstance(selected, list):
        selected = []
    if kind.startswith("piece_") and not selected and not p.get("allow_empty_topics"):
        # piece 允许空选题（Agent 匹配）；其它 kind 不需要选题
        pass

    brief: Dict[str, Any] = {
        "goal": goal,
        "topic": goal,
        "prompt": goal,
        "title": str(p.get("title") or goal).strip(),
        "audience": str(p.get("audience") or "").strip(),
        "actionId": "agent",
        "actionLabel": "本地 Agent 执行",
        "source": "agent",
        "output_type": kind,
        "quantity": quantity,
    }
    body: Dict[str, Any] = {
        "project_id": p["project_id"],
        "brief": brief,
        "output_type": kind,
        "quantity": quantity,
        "use_ai_topics": False,
        "skip_ai": True,
        "source": "agent",
        "selected_topics": selected if kind.startswith("piece_") else [],
    }
    if kind.startswith("piece_"):
        body["content_type_config"] = p.get("content_type_config") or p.get("contentTypeConfig") or _build_content_type_config(
            ct or "xiaohongshu", quantity
        )
    else:
        body["content_type_config"] = []

    if p.get("goal_id") or p.get("goalId"):
        body["goal_id"] = int(p.get("goal_id") or p.get("goalId"))

    st = str(p.get("schedule_type") or p.get("scheduleType") or "manual").strip() or "manual"
    body["schedule_type"] = st
    if p.get("schedule_config") is not None or p.get("scheduleConfig") is not None:
        body["schedule_config"] = p.get("schedule_config") or p.get("scheduleConfig")
    if p.get("schedule_enabled") is not None or p.get("scheduleEnabled") is not None:
        body["schedule_enabled"] = bool(
            p.get("schedule_enabled") if p.get("schedule_enabled") is not None else p.get("scheduleEnabled")
        )

    payload = request_api("POST", "/v1/project_task/create", body=body, timeout=120)
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or {}
    task_id = info.get("id") if isinstance(info, dict) else None
    result: Dict[str, Any] = {"info": info, "result": payload, "output_type": kind}
    if task_id is not None:
        result["taskId"] = int(task_id)
    if isinstance(info, dict) and info.get("topics"):
        result["topics"] = info["topics"]
    return result


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python content-task-create.py \'{"goal":"推广方向","output_type":"piece_xiaohongshu","selected_topics":[{"title":"选题A"}]}\'',
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
