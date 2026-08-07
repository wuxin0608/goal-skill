#!/usr/bin/env python3
"""edit-task：修改笔记任务标题与正文（edit/task），不修改配图"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_skill


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    raw_task_id = params.get("taskId")
    if raw_task_id is None:
        raise ValueError("缺少 taskId")
    task_id = int(raw_task_id)
    if task_id <= 0:
        raise ValueError("taskId 必须大于 0")

    title = str(params.get("title") or "").strip()
    text = str(params.get("text") or "").strip()
    if not title or not text:
        raise ValueError("缺少 title 或 text")

    body = {
        "taskId": task_id,
        "title": title,
        "text": text,
    }
    payload = request_skill("/v1/ainote/skill/edit/task", body)
    updated_id = payload.get("data", {}).get("id") or payload.get("id") or task_id
    return {
        "editResult": payload,
        "taskId": int(updated_id),
    }


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    title = None
    text = None

    if "--title" in argv:
        idx = argv.index("--title")
        if idx + 1 < len(argv):
            title = argv[idx + 1]
            argv = argv[:idx] + argv[idx + 2 :]

    if "--text" in argv:
        idx = argv.index("--text")
        if idx + 1 < len(argv):
            text = argv[idx + 1]
            argv = argv[:idx] + argv[idx + 2 :]

    if not argv:
        print(
            '用法: python edit-task.py \'{"taskId":98765,"title":"...","text":"..."}\'',
            file=sys.stderr,
        )
        return 1

    try:
        inp = json.loads(argv[0])
        if not isinstance(inp, dict):
            raise ValueError("参数必须是 JSON 对象")
        if title:
            inp["title"] = title
        if text:
            inp["text"] = text
        result = run(inp)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except json.JSONDecodeError as exc:
        print(json.dumps({"error": f"JSON 解析错误: {exc}"}, ensure_ascii=False))
        return 1
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
