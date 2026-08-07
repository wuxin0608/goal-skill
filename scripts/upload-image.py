#!/usr/bin/env python3
"""upload-image：上传本地图片并追加到 add-task 创建的笔记任务"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List

from common import request_skill_multipart

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}


def validate_image_path(path: str) -> str:
    abs_path = os.path.abspath(path)
    if not os.path.isfile(abs_path):
        raise ValueError(f"文件不存在: {path}")
    ext = os.path.splitext(abs_path)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的图片格式: {ext or '(无扩展名)'}")
    return abs_path


def run(params: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
    raw_task_id = params.get("taskId")
    if raw_task_id is None:
        raise ValueError("缺少 taskId")
    task_id = int(raw_task_id)
    if task_id <= 0:
        raise ValueError("taskId 必须大于 0")
    if not file_paths:
        raise ValueError("缺少本地图片路径")

    uploaded_urls: List[str] = []
    all_images: List[str] = []

    for path in file_paths:
        local_path = validate_image_path(path)
        payload = request_skill_multipart(
            "/v1/ainote/skill/add/task/photo",
            task_id,
            local_path,
        )
        data = payload.get("data") or {}
        url = str(data.get("url") or "").strip()
        images = data.get("images") or []
        if url:
            uploaded_urls.append(url)
        if isinstance(images, list):
            all_images = [str(item).strip() for item in images if str(item).strip()]

    return {
        "uploadResult": {
            "taskId": task_id,
            "urls": uploaded_urls,
            "images": all_images,
        }
    }


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload local images to ainote task photos.")
    parser.add_argument(
        "--params",
        required=True,
        help='JSON 参数，例如 {"taskId":98765}',
    )
    parser.add_argument("files", nargs="+", help="本地图片路径，可多张")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python upload-image.py --params \'{"taskId":98765}\' /path/a.jpg [/path/b.png ...]',
            file=sys.stderr,
        )
        return 1

    try:
        args = parse_args(argv)
        params = json.loads(args.params)
        if not isinstance(params, dict):
            raise ValueError("--params 必须是 JSON 对象")
        result = run(params, args.files)
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
