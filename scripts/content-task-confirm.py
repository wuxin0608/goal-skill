#!/usr/bin/env python3
"""content-task-confirm：已废弃 — 会触发后端 LLM，Agent 请改用 piece-create。"""

from __future__ import annotations

import json
import sys
from typing import List, Optional

DEPRECATED = (
    "content-task-confirm 已废弃：会触发后端模型生成。"
    "请由前端 Agent 本地写稿后调用 piece-create.py 落库。"
)


def main(argv: Optional[List[str]] = None) -> int:
    print(json.dumps({"error": DEPRECATED}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
