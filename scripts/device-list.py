#!/usr/bin/env python3
"""device-list：获取项目下所有设备并写入 .cache/devices.json"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List

from common import load_devices, request_skill, save_devices


def run() -> List[Dict[str, Any]]:
    payload = request_skill("/v1/ainote/skill/device/list", {})
    raw_list = payload.get("list") or payload.get("data", {}).get("list") or []
    devices: List[Dict[str, Any]] = []
    for item in raw_list:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        device_id = item.get("deviceId")
        url = str(item.get("url") or "").strip()
        if name and device_id is not None:
            devices.append({"name": name, "deviceId": device_id, "url": url})
    save_devices(devices)
    return devices


def main() -> int:
    try:
        devices = run()
        print(json.dumps({"devices": devices, "cached": True}, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
