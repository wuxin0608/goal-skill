#!/usr/bin/env python3
"""goal-diverge-finish：Skill 回写候选菜单（kind=candidate, pending）"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    run_id = params.get("run_id") or params.get("runId") or params.get("id")
    if run_id is None:
        raise ValueError("缺少 run_id / runId")
    run_id = int(run_id)
    if run_id <= 0:
        raise ValueError("run_id 必须大于 0")
    candidates = params.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("缺少 candidates 数组")
    payload = request_api(
        "POST",
        "/v1/project_task/diverge/finish",
        body={"run_id": run_id, "candidates": candidates},
        timeout=120,
    )
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or {}
    out: Dict[str, Any] = {"runId": run_id, "info": info}
    if isinstance(info, dict):
        out["count"] = info.get("count")
    return out


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python goal-diverge-finish.py \'{"run_id":789,"candidates":[...]}\'',
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
