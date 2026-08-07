#!/usr/bin/env python3
"""add-task：创建笔记任务（add/task）"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_skill, resolve_device_id, with_project_id


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    device_id = resolve_device_id(params)
    title = str(params.get("title") or "").strip()
    text = str(params.get("text") or "").strip()
    if not title or not text:
        raise ValueError("缺少 title 或 text")

    body = with_project_id(
        {
            "deviceId": device_id,
            "title": title,
            "text": text,
        }
    )
    payload = request_skill("/v1/ainote/skill/add/task", body)
    task_id = payload.get("data", {}).get("id") or payload.get("id")
    result: Dict[str, Any] = {"noteshareResult": payload}
    if task_id is not None:
        result["taskId"] = int(task_id)
    return result


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
            '用法: python add-task.py \'{"title":"...","text":"...","deviceId":123}\'',
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
