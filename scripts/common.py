#!/usr/bin/env python3
"""Shared helpers for goal-skill scripts."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
CACHE_DIR = os.path.join(SKILL_ROOT, ".cache")
DEVICES_CACHE = os.path.join(CACHE_DIR, "devices.json")
PROJECT_CACHE = os.path.join(CACHE_DIR, "project.json")

DEFAULT_API_BASE = "https://ai2027.cn/goal/web"
API_BASE = (os.environ.get("AIGOAL_API_BASE") or DEFAULT_API_BASE).rstrip("/")
API_KEY_HEADER = "X-AIGOAL-API-KEY"
SUCCESS_CODE = 20000


def get_api_key() -> str:
    key = os.environ.get("AIGOAL_API_KEY", "").strip()
    if not key:
        raise ValueError("缺少 AIGOAL_API_KEY，请设置环境变量 AIGOAL_API_KEY")
    return key


def _check_payload(payload: Dict[str, Any]) -> Any:
    code = payload.get("code")
    if code is not None and code != SUCCESS_CODE:
        message = payload.get("message") or str(payload)
        raise ValueError(f"API 错误: code={code}, message={message}")
    return payload


def _session() -> requests.Session:
    # 避免系统代理把 localhost / 内网请求打成 502
    s = requests.Session()
    s.trust_env = False
    return s


def request_api(
    method: str,
    path: str,
    *,
    body: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 60,
) -> Any:
    api_key = get_api_key()
    url = f"{API_BASE}{path}"
    headers = {API_KEY_HEADER: api_key}
    method_u = method.upper()
    session = _session()
    if method_u == "GET":
        response = session.get(url, params=params or {}, headers=headers, timeout=timeout)
    elif method_u == "POST":
        response = session.post(
            url,
            json=body if body is not None else {},
            params=params,
            headers=headers,
            timeout=timeout,
        )
    else:
        raise ValueError(f"不支持的 HTTP 方法: {method}")
    response.raise_for_status()
    payload = response.json() if response.text else {}
    return _check_payload(payload)


def request_skill(path: str, body: Optional[Dict[str, Any]] = None) -> Any:
    """POST to /v1/ainote/skill/* (legacy publish APIs)."""
    return request_api("POST", path, body=body or {}, timeout=30)


def request_skill_multipart(path: str, task_id: int, file_path: str) -> Any:
    api_key = get_api_key()
    if task_id <= 0:
        raise ValueError("taskId 必须大于 0")
    if not os.path.isfile(file_path):
        raise ValueError(f"文件不存在: {file_path}")

    url = f"{API_BASE}{path}"
    with open(file_path, "rb") as file_obj:
        response = _session().post(
            url,
            data={"taskId": str(task_id)},
            files={"file": (os.path.basename(file_path), file_obj)},
            headers={API_KEY_HEADER: api_key},
            timeout=120,
        )
    response.raise_for_status()
    payload = response.json() if response.text else {}
    return _check_payload(payload)


def ensure_cache_dir() -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)


def load_devices() -> List[Dict[str, Any]]:
    if not os.path.isfile(DEVICES_CACHE):
        return []
    with open(DEVICES_CACHE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in data:
        if isinstance(item, dict):
            name = str(item.get("name") or "").strip()
            device_id = item.get("deviceId")
            url = str(item.get("url") or "").strip()
            if name and device_id is not None:
                out.append({"name": name, "deviceId": device_id, "url": url})
    return out


def save_devices(devices: List[Dict[str, Any]]) -> None:
    ensure_cache_dir()
    with open(DEVICES_CACHE, "w", encoding="utf-8") as f:
        json.dump(devices, f, ensure_ascii=False, indent=2)


def load_project() -> Optional[Dict[str, Any]]:
    if not os.path.isfile(PROJECT_CACHE):
        return None
    with open(PROJECT_CACHE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        return None
    project_id = data.get("projectId") or data.get("project_id")
    if project_id is None:
        return None
    try:
        pid = int(project_id)
    except (TypeError, ValueError):
        return None
    if pid <= 0:
        return None
    return {
        "projectId": pid,
        "name": str(data.get("name") or "").strip(),
    }


def save_project(project_id: int, name: str = "") -> None:
    ensure_cache_dir()
    with open(PROJECT_CACHE, "w", encoding="utf-8") as f:
        json.dump(
            {"projectId": int(project_id), "name": str(name or "").strip()},
            f,
            ensure_ascii=False,
            indent=2,
        )


def resolve_project_id(params: Optional[Dict[str, Any]] = None) -> int:
    params = params or {}
    for key in ("projectId", "project_id"):
        raw = params.get(key)
        if raw is not None:
            project_id = int(raw)
            if project_id > 0:
                return project_id
            raise ValueError("projectId 必须大于 0")

    cached = load_project()
    if cached:
        return int(cached["projectId"])
    raise ValueError("缺少 projectId，请先运行 project-list.py / project-use.py")


def with_project_id(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return a shallow copy of params ensuring project_id is set."""
    out = dict(params or {})
    pid = resolve_project_id(out)
    out["project_id"] = pid
    out["projectId"] = pid
    return out


def resolve_device_id(params: Optional[Dict[str, Any]] = None) -> int:
    params = params or {}
    raw_id = params.get("deviceId")
    if raw_id is not None:
        device_id = int(raw_id)
        if device_id > 0:
            return device_id
        raise ValueError("deviceId 必须大于 0")

    device_name = str(params.get("deviceName") or params.get("name") or "").strip()
    devices = load_devices()
    if device_name:
        for item in devices:
            if item.get("name") == device_name:
                return int(item["deviceId"])
        raise ValueError(f"devices.json 中不存在设备: {device_name}")

    if len(devices) == 1:
        return int(devices[0]["deviceId"])
    if not devices:
        raise ValueError("缺少 deviceId，请先运行 device-list.py 生成 .cache/devices.json")
    names = ", ".join(item["name"] for item in devices)
    raise ValueError(f"存在多个设备，请指定 deviceName 或 deviceId。可选: {names}")


def resolve_publish_key(params: Optional[Dict[str, Any]] = None) -> str:
    params = params or {}
    for key in ("publishKey", "deviceUrl", "url"):
        value = params.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    device_name = str(params.get("deviceName") or params.get("name") or "").strip()
    devices = load_devices()
    if device_name:
        for item in devices:
            if item.get("name") == device_name and item.get("url"):
                return str(item["url"])
        raise ValueError(f"devices.json 中不存在设备: {device_name}")

    if len(devices) == 1 and devices[0].get("url"):
        return str(devices[0]["url"])
    if not devices:
        raise ValueError("缺少 publishKey，请先运行 device-list.py 生成 .cache/devices.json")
    names = ", ".join(item["name"] for item in devices)
    raise ValueError(f"存在多个设备，请指定 deviceName。可选: {names}")


def parse_publish_key(publish_key: str) -> Dict[str, str]:
    parsed = urlparse(publish_key.strip())
    query = parsed.query
    values = {}
    for part in query.split("&"):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        values[k] = v
    app_key = values.get("appkey", "").strip()
    tag = values.get("tag", "").strip()
    if not app_key:
        raise ValueError("publishKey URL 缺少 appkey 参数")
    return {"appkey": app_key, "tag": tag}


def parse_json_arg(argv: List[str]) -> Dict[str, Any]:
    """Parse CLI: either raw JSON, or --params '{...}'."""
    if not argv:
        return {}
    if "--params" in argv:
        idx = argv.index("--params")
        if idx + 1 >= len(argv):
            raise ValueError("缺少 --params 的 JSON 参数")
        raw = argv[idx + 1]
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("参数必须是 JSON 对象")
        return data
    data = json.loads(argv[0])
    if not isinstance(data, dict):
        raise ValueError("参数必须是 JSON 对象")
    return data


def cli_main(run_fn, usage: str) -> int:
    import sys

    argv = list(sys.argv[1:])
    try:
        params = parse_json_arg(argv) if argv else {}
        result = run_fn(params)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except json.JSONDecodeError as exc:
        print(json.dumps({"error": f"JSON 解析错误: {exc}"}, ensure_ascii=False))
        return 1
    except Exception as exc:
        if not argv and usage:
            print(usage, file=sys.stderr)
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1
