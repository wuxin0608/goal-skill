#!/usr/bin/env python3
"""task-candidate-select：采纳/拒绝/延期候选（通常由 Web 操作；Skill 可选）"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    cand_id = params.get("id") or params.get("candidateId") or params.get("taskId")
    if cand_id is None:
        raise ValueError("缺少 id")
    cand_id = int(cand_id)
    action = str(params.get("action") or "").strip().lower()
    if action not in ("accept", "reject", "defer"):
        raise ValueError("action 必须是 accept|reject|defer")
    payload = request_api(
        "POST",
        "/v1/project_task/candidate/select",
        body={"id": cand_id, "action": action},
    )
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or {}
    return {"id": cand_id, "action": action, "info": info}


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python task-candidate-select.py \'{"id":123,"action":"accept"}\'',
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
