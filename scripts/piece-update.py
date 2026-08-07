#!/usr/bin/env python3
"""piece-update：修改成稿文案"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    piece_id = params.get("id") or params.get("pieceId") or params.get("piece_id")
    if piece_id is None:
        raise ValueError("缺少 id（piece id）")
    piece_id = int(piece_id)
    if piece_id <= 0:
        raise ValueError("id 必须大于 0")
    if "result" not in params:
        raise ValueError("缺少 result（成稿正文）")
    result_text = str(params.get("result") or "")

    payload = request_api(
        "POST",
        "/v1/project_piece/update",
        body={"id": piece_id, "result": result_text},
    )
    return {"id": piece_id, "result": payload}


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python piece-update.py \'{"id":1,"result":"新的成稿正文"}\'',
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
