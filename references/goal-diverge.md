# Goal 发散候选约定

本地 Agent 根据项目 Goal + 资料/选题生成候选后，经 `goal-diverge-finish` 写入。

完整 kind 列表见 [`artifact-kinds.md`](artifact-kinds.md)。

## 原则

- **只根据固定 Goal 与现有资料/选题发散**，禁止根据赞、藏、评论等 metrics 改目标或选题。
- 后端不调用 LLM；发散与写稿均在本地完成。
- 用户在 Web「候选菜单」勾选后，按 `output_type`（扁平 kind）进入对应回写链路。

## `candidates[]` 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 菜单展示标题 |
| `output_type` | string | **扁平 kind**：`piece_xiaohongshu` / `file_md` / `topic` / `photo` / `template` / `speech` / `subgoal` 等 |
| `prompt` | string | 执行时 brief 提示 |
| `why` | string | 可选，推荐理由 |
| `quantity` | number | 可选，期望产物数 |
| `assignee` | string | 默认 `agent`；可 `human` |
| `tasks` | array | **仅 `subgoal`**：同时创建的新目标菜单候选（字段同本表，勿再嵌套 subgoal） |

**不要**再传 `content_types`（旧两层模型）。若误传 `output_type=copy` + `content_types`，后端会归一成 `piece_*`。

**`subgoal` + `tasks`（推荐）**：finish 时会**同时**创建 `pending_review` 目标，并把 `tasks` 写成挂在该新目标下的候选菜单。也可对已有 `pending_review` 目标直接 `goal-diverge-trigger` 写菜单。

## 示例

```json
{
  "run_id": 789,
  "candidates": [
    {
      "title": "周末一人食探店",
      "output_type": "piece_xiaohongshu",
      "prompt": "围绕一人周末探店写小红书，语气轻松",
      "why": "贴合本周小目标",
      "quantity": 3,
      "assignee": "agent"
    },
    {
      "title": "拆 5 个周末选题",
      "output_type": "topic",
      "prompt": "从资料拆可写选题入库",
      "quantity": 5
    },
    {
      "title": "本周攻「一个人周末」",
      "output_type": "subgoal",
      "prompt": "建议新增小目标：聚焦一人周末场景",
      "tasks": [
        {
          "title": "周末一人食探店",
          "output_type": "piece_xiaohongshu",
          "prompt": "围绕一人周末探店写小红书",
          "quantity": 3
        },
        {
          "title": "拆 5 个周末选题",
          "output_type": "topic",
          "quantity": 5
        }
      ]
    },
    {
      "title": "补充竞品结构笔记",
      "output_type": "file_md",
      "prompt": "把对标拆解写成 md 资料",
      "quantity": 1
    }
  ]
}
```
