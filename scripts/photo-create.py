#!/usr/bin/env python3
"""photo-create：上传本地图（可选）并写入 project_photos"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional

from common import API_BASE, API_KEY_HEADER, _check_payload, _session, get_api_key, request_api, with_project_id

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}


def _upload_local(path: str) -> str:
    abs_path = os.path.abspath(path)
    if not os.path.isfile(abs_path):
        raise ValueError(f"文件不存在: {path}")
    ext = os.path.splitext(abs_path)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的图片格式: {ext or '(无扩展名)'}")
    api_key = get_api_key()
    url = f"{API_BASE}/v1/upload/image"
    with open(abs_path, "rb") as file_obj:
        response = _session().post(
            url,
            data={"group": "project"},
            files={"file": (os.path.basename(abs_path), file_obj)},
            headers={API_KEY_HEADER: api_key},
            timeout=120,
        )
    response.raise_for_status()
    payload = _check_payload(response.json() if response.text else {})
    data = payload.get("data") or payload.get("info") or payload
    if isinstance(data, dict):
        for key in ("url", "src", "path"):
            u = str(data.get(key) or "").strip()
            if u:
                return u
    raise ValueError(f"上传成功但未返回 url: {payload}")


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    p = with_project_id(params)
    url = str(p.get("url") or "").strip()
    file_path = str(p.get("file") or p.get("path") or p.get("localPath") or "").strip()
    if not url and file_path:
        url = _upload_local(file_path)
    if not url:
        raise ValueError("缺少 url 或本地 file 路径")
    name = str(p.get("name") or os.path.basename(file_path) or "photo").strip()
    body = {
        "project_id": p["project_id"],
        "url": url,
        "name": name,
    }
    payload = request_api("POST", "/v1/project_photos/create", body=body, timeout=60)
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or payload
    photo_id = None
    if isinstance(info, dict):
        photo_id = info.get("id")
    return {"id": photo_id, "url": url, "name": name, "info": info, "result": payload}


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python photo-create.py \'{"projectId":1,"file":"/tmp/a.png"}\' '
            '或 \'{"projectId":1,"url":"https://..."}\'',
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
