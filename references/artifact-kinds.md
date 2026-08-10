# 扁平产物 Kind（artifact kind）

任务 / 候选的产物形态存在 `project_task.output_type`，使用**扁平 kind**（不再使用 `copy` + `content_types[]` 两层）。

## 列表

| kind | 族 | sink | 默认数量 |
|------|-----|------|----------|
| `piece_*`（10 种渠道文案） | piece | `project_piece` | 4 |
| `file_md` / `file_txt` / `file_html` | file | `project_files` | 1 |
| `topic` | topic | `project_topics` | 5 |
| `photo` | photo | OSS + `project_photos` | 4 |
| `template` | template | `project_templates` | 3 |
| `subgoal` | subgoal | `project_goals` | 1 |
| `speech` | speech | `project_speech` | 5 |

### 文案 vs 话术（勿混用）

| | 文案 `piece_*` | 话术 `speech` |
|--|----------------|---------------|
| 用途 | 公域/私域渠道成稿（笔记、朋友圈、社群、海报、生图提示等） | 一对一发送：私聊破冰、活动邀约等 |
| 形态 | 单条 `result` 正文 | `title` + `copies[]`（多条可替换变体） |
| 列表 | 文案列表 / 文案组 | 话术列表 / 话术组 |
| 键盘 | 文案 Tab | 话术 Tab |

完整 `piece_*`：去掉前缀 `piece_` 即为原 `content_type`（见 `content-formats.md` 的 piece 小节）。话术写法见同文件 **`speech`** 小节。

Web 创建任务分组：**公域文案 / 私域文案 / 项目文件 / 其他**（`speech` 在「其他」）。

## 旧值归一

| 旧值 | 新 kind |
|------|---------|
| `copy` / `private_script` + `content_types[0]=T` | `piece_T` |
| 空 + `content_type_config` 启用 T | `piece_T` |
| `structure` | `file_md` |

## 候选 finish 字段

```json
{
  "title": "…",
  "output_type": "piece_xiaohongshu",
  "prompt": "…",
  "why": "…",
  "quantity": 4,
  "assignee": "agent"
}
```

勿再传 `content_types`（后端若收到旧字段会归一）。话术候选用 `"output_type": "speech"`。

## 执行分支（claim 后）

- `piece_*` → `piece-create` ×N → `content-task-finish`
- `topic` → `topic-create` ×N → finish（`generated_count` / `artifact_ids`）
- `file_*` → `file-upsert` → finish
- `photo` → `photo-create` ×N → finish
- `template` → `template-upsert` 或链接 `add-template` → finish
- `speech` → `speech-create` ×N（`title` + `copies[]`）→ finish（`generated_count` / `artifact_ids`）
- `subgoal` → Web 采纳时建 `pending_review` 目标；发散 finish 时若带 `tasks` 则同时创建目标 + 菜单候选

### `speech-create` 要点

```json
{
  "title": "破冰开场",
  "copies": ["你好呀，看到你也关注…", "方便聊两句吗？"],
  "project_speech_group_id": 123
}
```

- `copies` 至少 1 条；可省略 `project_speech_group_id`（脚本会用「默认话术」组，没有则创建）。
- 一条 `speech` 记录 = 一个话术条目（多条文案变体）；`quantity=N` 表示创建 N 条话术记录。
- 写稿规则：`Read references/content-formats.md` 的 **`speech`** 小节。
