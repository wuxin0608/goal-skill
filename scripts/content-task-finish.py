#!/usr/bin/env python3
"""content-task-finish：结束本批执行并回写 run_state"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    task_id = params.get("taskId") or params.get("id") or params.get("project_task_id")
    if task_id is None:
        raise ValueError("缺少 taskId")
    task_id = int(task_id)
    if task_id <= 0:
        raise ValueError("taskId 必须大于 0")
    body: Dict[str, Any] = {"id": task_id}
    for src, dst in (
        ("batch_tag", "batch_tag"),
        ("batchTag", "batch_tag"),
        ("failed", "failed"),
        ("error", "error"),
        ("message", "error"),
        ("generated_count", "generated_count"),
        ("generatedCount", "generated_count"),
        ("artifact_ids", "artifact_ids"),
        ("artifactIds", "artifact_ids"),
    ):
        if params.get(src) is not None and dst not in body:
            body[dst] = params[src]
    payload = request_api("POST", "/v1/project_task/finish", body=body, timeout=60)
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or {}
    out: Dict[str, Any] = {"taskId": task_id, "info": info}
    if isinstance(info, dict):
        out["success"] = bool(info.get("success"))
        out["generated_piece_count"] = info.get("generated_piece_count")
        out["expected_piece_count"] = info.get("expected_piece_count")
        out["batch_tag"] = info.get("batch_tag")
    return out


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python content-task-finish.py \'{"taskId":123,"batch_tag":"..."}\'',
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
