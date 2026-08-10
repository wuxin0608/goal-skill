#!/usr/bin/env python3
"""Rebuild speech groups + speeches for 异性沟通SOP (project 65)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from common import request_api, with_project_id  # noqa: E402


def _load_run(filename: str):
    path = SCRIPT_DIR / filename
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载 {filename}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.run


speech_create = _load_run("speech-create.py")
speech_group_create = _load_run("speech-group-create.py")

STAGES = [
    {
        "title": "①破冰开场",
        "sort_order": 10,
        "speeches": [
            {
                "title": "意见开场·小争辩",
                "copies": [
                    "帮我断一下这个局",
                    "朋友俩人吵：第一次约会该谁付钱",
                    "你站哪边？别讲正确答案，讲你真实想法",
                ],
            },
            {
                "title": "意见开场·前男友边界",
                "copies": [
                    "问个有点现实的问题",
                    "如果男生跟前女友还处得特别好，你会继续跟他约会吗",
                    "你更在意忠诚，还是更在意他会不会社交干净",
                ],
            },
            {
                "title": "意见开场·纹身",
                "copies": [
                    "临时裁决一下",
                    "纹身和穿环，你觉得哪个更加分",
                    "你自己有没有想过动手，还是只敢欣赏别人",
                ],
            },
            {
                "title": "情境开场·刷到你",
                "copies": [
                    "刚刷到你发的那个",
                    "我本来滑过去了，结果又滑回来",
                    "就问一句：你那天是认真的，还是随手发的",
                ],
            },
            {
                "title": "直接但不油",
                "copies": [
                    "直说吧",
                    "想认识你一下，不是来尬聊工作的那种",
                    "你现在方便回两句吗，忙的话我晚点找你",
                ],
            },
            {
                "title": "好奇开场·空闲一天",
                "copies": [
                    "假设你突然有一天完全空闲",
                    "什么安排都可以，你会怎么过",
                    "别说睡觉，那个答案太偷懒",
                ],
            },
            {
                "title": "见好就收·破冰收尾",
                "copies": [
                    "今天先聊到这",
                    "你挺有意思的，我记下了",
                    "忙你的，别秒回我",
                ],
            },
        ],
    },
    {
        "title": "②轻松升温",
        "sort_order": 20,
        "speeches": [
            {
                "title": "轻推拉·有点危险",
                "copies": [
                    "你这个回复有点危险",
                    "再聊下去我怕周末要腾时间",
                    "先到这，留一点悬念给你",
                ],
            },
            {
                "title": "轻推拉·夸完就停",
                "copies": [
                    "你刚才那个点挺加分",
                    "认真说，比我预期有趣一点",
                    "夸完了，今天额度用完",
                ],
            },
            {
                "title": "情绪·像小孩说话",
                "copies": [
                    "哼，你这句有点欠",
                    "我记下了，回头要讨回来",
                    "不过今天先放过你",
                ],
            },
            {
                "title": "陈述代替提问",
                "copies": [
                    "我周末本来打算宅翻车",
                    "结果又被朋友拖出门了",
                    "你那种更像出门派，还是窝着充电派",
                ],
            },
            {
                "title": "轻微打压测反应",
                "copies": [
                    "你看起来挺乖的",
                    "但我猜你偶尔也会很坏",
                    "猜错了你就纠正我",
                ],
            },
            {
                "title": "升温后抽离",
                "copies": [
                    "聊得还行",
                    "但我不打算把你聊成重点位",
                    "就当认识了个有趣的人，行不行",
                ],
            },
            {
                "title": "见好就收·升温收尾",
                "copies": [
                    "这个话题再往下就太顺了",
                    "我先撤一步",
                    "你要是还想聊，下次你起个头",
                ],
            },
        ],
    },
    {
        "title": "③舒适信任",
        "sort_order": 30,
        "speeches": [
            {
                "title": "童年锚点",
                "copies": [
                    "你七岁左右最想当什么",
                    "我那会儿想当导演，在手心乱画分镜给家里人看",
                    "你那会儿的愿望，现在还留着几分",
                ],
            },
            {
                "title": "带我去哪",
                "copies": [
                    "如果只能带我去一个地方",
                    "不限远近，你会选哪",
                    "理由比地名重要",
                ],
            },
            {
                "title": "反差共鸣",
                "copies": [
                    "你给人第一印象偏酷一点",
                    "但我感觉私下会更软一点",
                    "说错了你就打我",
                ],
            },
            {
                "title": "生活状态",
                "copies": [
                    "最近状态怎么样",
                    "不是客套，是真的想知道你累不累",
                    "飞得高不高别人问得多，飞得累不累很少人问",
                ],
            },
            {
                "title": "同步又留空间",
                "copies": [
                    "有时候觉得我们节奏挺像",
                    "这挺少见的",
                    "所以更要慢一点，别一下聊穿",
                ],
            },
            {
                "title": "信任边界",
                "copies": [
                    "你好像对人不容易完全松开",
                    "这不算冷漠，更像学会了自保",
                    "我尊重这个，不硬撬",
                ],
            },
            {
                "title": "舒适收尾",
                "copies": [
                    "今天这几句够了",
                    "留点下次再说",
                    "晚安，别想太多",
                ],
            },
        ],
    },
    {
        "title": "④邀约推进",
        "sort_order": 40,
        "speeches": [
            {
                "title": "主导邀约·半小时试聊",
                "copies": [
                    "周六下午我想去 XX 喝一杯",
                    "就当半小时试聊，不爽随时撤",
                    "你直接回个大概时间，我按你方便定",
                ],
            },
            {
                "title": "主导邀约·店",
                "copies": [
                    "XX 有家店我想去试",
                    "你过来一起，别整正式约会那套",
                    "行就回「时间」，不行就说「下次」",
                ],
            },
            {
                "title": "邀约·拒绝后换说法",
                "copies": [
                    "吃夜宵就算了",
                    "那你过来，带你去个轻松点的地方",
                    "不勉强，就看你想不想出门",
                ],
            },
            {
                "title": "收联系方式",
                "copies": [
                    "今天先到这",
                    "你方便的联系方式给我一个",
                    "我找个双方都不赶的时间，把刚才那个话题续上",
                ],
            },
            {
                "title": "确认赴约",
                "copies": [
                    "那就按这个时间见",
                    "我提前十分钟到",
                    "你到了跟我说一声就行",
                ],
            },
            {
                "title": "见面后复盘升温",
                "copies": [
                    "今天挺好的",
                    "比微信里更真实一点",
                    "下次我想换个更安静的地方",
                ],
            },
            {
                "title": "踩雷·有对象",
                "copies": [
                    "那挺好，说明你有人欣赏",
                    "我不是来抢位置的，就聊天",
                    "有对象也能好好说话吧，不行我退",
                ],
            },
        ],
    },
]


def _unwrap_list(payload):
    data = payload.get("data") or payload
    return data.get("list") or payload.get("list") or []


def list_speech_groups(project_id: int):
    payload = request_api("GET", "/v1/project_speech_groups/list", params={"project_id": project_id})
    return [g for g in _unwrap_list(payload) if isinstance(g, dict)]


def list_speeches(project_id: int, group_id: int = 0):
    params = {"project_id": project_id}
    if group_id:
        params["group_id"] = group_id
    payload = request_api("GET", "/v1/project_speech/list", params=params)
    return [s for s in _unwrap_list(payload) if isinstance(s, dict)]


def soft_delete_all(project_id: int) -> dict:
    deleted_groups = []
    deleted_speeches = []
    for g in list_speech_groups(project_id):
        gid = int(g["id"])
        for s in list_speeches(project_id, gid):
            sid = int(s["id"])
            request_api(
                "POST",
                "/v1/project_speech/delete",
                body={"id": sid, "project_id": project_id},
            )
            deleted_speeches.append(sid)
        request_api(
            "POST",
            "/v1/project_speech_groups/delete",
            body={"id": gid, "project_id": project_id},
        )
        deleted_groups.append({"id": gid, "title": g.get("title")})
    return {"deletedGroups": deleted_groups, "deletedSpeechIds": deleted_speeches}


def create_all(project_id: int) -> list:
    out = []
    for stage in STAGES:
        g = speech_group_create(
            {"project_id": project_id, "title": stage["title"], "sort_order": stage["sort_order"]}
        )
        gid = int(g["groupId"])
        created = []
        for i, sp in enumerate(stage["speeches"]):
            r = speech_create(
                {
                    "project_id": project_id,
                    "project_speech_group_id": gid,
                    "title": sp["title"],
                    "copies": sp["copies"],
                    "sort_order": i,
                }
            )
            created.append(
                {"title": sp["title"], "speechId": r.get("speechId"), "copies": len(sp["copies"])}
            )
        out.append({"title": stage["title"], "groupId": gid, "speeches": created})
    return out


def main() -> int:
    p = with_project_id({"project_id": 65})
    project_id = int(p["project_id"])
    deleted = soft_delete_all(project_id)
    groups = create_all(project_id)
    summary = {
        "projectId": project_id,
        "deleted": deleted,
        "groups": groups,
        "groupCount": len(groups),
        "speechCount": sum(len(g["speeches"]) for g in groups),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
