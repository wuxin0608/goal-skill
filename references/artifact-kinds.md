# 扁平产物 Kind（artifact kind）

任务 / 候选的产物形态存在 `project_task.output_type`，使用**扁平 kind**（不再使用 `copy` + `content_types[]` 两层）。

## 列表

| kind | 族 | sink | 默认数量 |
|------|-----|------|----------|
| `piece_xiaohongshu` …（12 种渠道） | piece | `project_piece` | 4（私聊 10） |
| `file_md` / `file_txt` / `file_html` | file | `project_files` | 1 |
| `topic` | topic | `project_topics` | 5 |
| `photo` | photo | OSS + `project_photos` | 4 |
| `template` | template | `project_templates` | 3 |
| `subgoal` | subgoal | `project_goals` | 1 |

完整 `piece_*` 与渠道对应：去掉前缀 `piece_` 即为原 `content_type`（见 `content-formats.md`）。

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

勿再传 `content_types`（后端若收到旧字段会归一）。

## 执行分支（claim 后）

- `piece_*` → `piece-create` ×N → `content-task-finish`
- `topic` → `topic-create` ×N → finish（`generated_count` / `artifact_ids`）
- `file_*` → `file-upsert` → finish
- `photo` → `photo-create` ×N → finish
- `template` → `template-upsert` 或链接 `add-template` → finish
- `subgoal` → Web 采纳时建 `pending_review` 目标；发散 finish 时若带 `tasks` 则同时创建目标 + 菜单候选
