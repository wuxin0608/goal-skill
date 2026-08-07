# Goal 发散候选约定

本地 Agent 根据项目 Goal + 资料/选题生成候选后，经 `goal-diverge-finish` 写入。

## 原则

- **只根据固定 Goal 与现有资料/选题发散**，禁止根据赞、藏、评论等 metrics 改目标或选题。
- 后端不调用 LLM；发散与写稿均在本地完成。
- 用户在 Web「候选菜单」勾选后，`copy` 类候选进入现有 claim / piece / finish 写稿链路。

## `candidates[]` 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 菜单展示标题 |
| `output_type` | string | `copy` / `topic` / `subgoal` / `private_script` 等 |
| `prompt` | string | 执行时 brief 提示（写稿/落选题用） |
| `why` | string | 可选，推荐理由 |
| `content_types` | string[] | `copy` 时建议带，如 `["xiaohongshu"]` |
| `assignee` | string | 默认 `agent`；可 `human` |

## 示例

```json
{
  "run_id": 789,
  "candidates": [
    {
      "title": "周末一人食探店",
      "output_type": "copy",
      "prompt": "围绕一人周末探店写小红书，语气轻松",
      "why": "贴合本周小目标",
      "content_types": ["xiaohongshu"],
      "assignee": "agent"
    },
    {
      "title": "本周攻「一个人周末」",
      "output_type": "subgoal",
      "prompt": "建议新增小目标：聚焦一人周末场景"
    }
  ]
}
```
