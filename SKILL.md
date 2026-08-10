---
name: goal-skill
description: goal-skill / 内容运营：按 Web 复制的 taskId= / projectId= 或今日 due 拉取任务并本地写稿回写；维护资料与选题；设备笔记发布；固定目标下 goal-diverge 写候选菜单。Use when user says 用 goal-skill 执行任务 taskId=… or 依次执行任务 taskId=… or 拉取并执行今日到期任务 or 用 goal-skill 对本项目发散 goal projectId=…. NEVER trigger backend LLM generation.
version: 3.6.0
author: custom
type: automation
permissions:
  - network
  - file.read
input_schema:
  type: object
  properties:
    tool:
      type: string
      description: 子能力名（如 `content-task-due` / `content-task-claim` / `piece-create` / `goal-diverge-finish`）
    params:
      type: object
      description: 对应子能力的参数对象
  required: [tool]
output_schema:
  type: object
  properties:
    result:
      type: object
    error:
      type: string
---

## 核心原则（必读）

**Web 只提交任务与调度配置；选题匹配与写稿一律由本地 Agent + 本 Skill 完成。后端只做存储与状态机，不调用任何模型。**

**产物用扁平 `output_type`（artifact kind）**：`piece_*` / `file_*` / `topic` / `photo` / `template` / `subgoal` / `speech`。列表见 [`references/artifact-kinds.md`](references/artifact-kinds.md)。

**`piece-create` 的 `result` = 渠道成品正文**（可直接复制粘贴发布/发送）。`piece_*` 对应的渠道格式见 [`references/content-formats.md`](references/content-formats.md)（章节名为去掉 `piece_` 后的 content_type）。

**固定目标发散：只根据 Goal + 资料/选题生成候选；禁止根据赞藏评论等 metrics 改目标或选题。** 候选字段见 [`references/goal-diverge.md`](references/goal-diverge.md)。

### Web 提示词识别（固定格式，按此解析）

Web「复制执行提示词」只会给出极短文本，形态固定为 **空格分隔的 `key=value`**：

| 用户粘贴的提示词 | 你必须做的事 |
|------------------|--------------|
| `用 goal-skill 执行任务 taskId=123 projectId=456` | 只跑 **这一个** taskId（流程 A0） |
| `用 goal-skill 依次执行任务 taskId=1,2,3 projectId=456` | 按列表 **挨个** A0；**不要**再调 `content-task-due` 覆盖列表 |
| `用 goal-skill 拉取并执行今日到期任务 projectId=456` | `content-task-due` → 对返回列表挨个 A0 |
| `用 goal-skill 对本项目发散 goal projectId=456 goalId=12` | 流程 D：对该目标发散写候选 |
| `用 goal-skill 对本项目发散 goal projectId=456 goalId=12 runId=789` | 流程 D：跳过 trigger，直接 finish |

解析规则：

1. 用正则提取 `taskId=` 后的数字；若含逗号（如 `1,2,3`）则拆成多个 id。
2. 提取 **`projectId=`（多项目用户必填）**；有则先 `project-use`（仅本地缓存当前项目，服务端不存默认项目）。
3. **有 `taskId` 时禁止再调 `content-task-due`**——Web 已给出要执行的 id。
4. 无 `taskId` 且出现「今日到期 / due」时，才走 `content-task-due`（须带 `projectId`）。
5. 出现「发散 goal」或 `goal-diverge` 时走流程 D；可提取可选 `runId=`。

**工作流细节由本 Skill 内置，不必写在提示词里。**

- ✅ 收到 `taskId` → `content-task-get` → `claim` → **按 output_type 族回写** → `finish`
- ✅ 或 `content-task-due` → **挨个** claim / 回写 / finish
- ✅ `piece_*` 无选题时：`topic-list` 按 brief.goal 本地匹配后再写
- ✅ 发散：candidates 使用扁平 kind → `goal-diverge-finish`
- ❌ **禁止** `content-task-confirm`（会触发后端 LLM）
- ❌ **禁止**任何后端 generate / 云端写稿接口
- ❌ **禁止**根据 metrics / 赞藏改 Goal 或选题

## 配置

设置环境变量 **`AIGOAL_API_KEY`**（`sk-` 前缀）。

- Key 为用户级固定密钥：Web 端「AI Agent 接入」复制。
- API 地址：`https://ai2027.cn/goal/web`（可用环境变量 `AIGOAL_API_BASE` 覆盖）
- 请求头：`X-AIGOAL-API-KEY`（需 VIP）

## 推荐流程

### A0. 执行指定 taskId（Web「复制执行提示词」主路径）

对每个 `taskId`：

1. 若提示词含 `projectId`：`project-use`
2. `content-task-get`（`taskId`）读 `output_type` / brief / topics / `content_type_config` / 项目
3. `content-task-claim` → `batch_tag`；若 `claimed=false` 则跳过并说明 reason
4. 按 **`output_type` 族**分支（见下）；数量用 `expected_piece_count` / `brief.quantity`
5. `content-task-finish`：`piece_*` 带 `batch_tag`；其它族带 `generated_count` 与可选 `artifact_ids`
6. 提示用户回 Web 工作台**手动刷新**任务列表

#### 按族回写

| output_type | 动作 |
|-------------|------|
| `piece_*` | 去前缀得 content_type；`Read content-formats.md`；topics 空则 `topic-list` 匹配；`piece-create` ×N（同 batch_tag）→ finish |
| `topic` | `topic-create` ×N → finish（`generated_count` / ids） |
| `file_md` / `file_txt` / `file_html` | 写内容 → `file-upsert`（扩展名随 kind）→ finish |
| `photo` | 生图或取本地图 → `photo-create` ×N → finish |
| `template` | 结构化 `template-upsert` 或链接 `keyword` 导入 → finish |
| `speech` | 写话术 → `speech-create` ×N（`title` + `copies[]`）→ finish（`generated_count` / ids） |
| `subgoal` | 通常 Web 已建目标；若仍 queued 可建 goal 后 finish |

### A. 执行今日到期任务（无 taskId 时）

| `schedule_type` | 含义 | Skill 何时领取 |
|-----------------|------|----------------|
| `manual` | 立即执行 | `pending_content` 且空闲时即到期 |
| `daily` | 每天循环 | `schedule_enabled` 且 `next_trigger_at <= now`；领取后算次日 |
| `weekly` | 每周循环 | 同上；领取后算下周 |
| `once` | 定时一次（旧数据） | 同上；领取后关闭调度 |

1. 可选 `project-use`（若有 `projectId`）
2. `content-task-due`（可选 `projectId`）→ 到期列表
3. **对每个任务挨个**走 A0
4. Web 列表手动刷新看 `run_state` 与成稿

### B. Agent 选题确认后建任务（可选）

1. 本地起草选题 → **用户确认**
2. `content-task-create`（`goal` + 可选 `selected_topics`，可带 `schedule_type`：manual/daily/weekly）
3. 再走流程 A / A0

### C. 小红书发布

1. `device-list` → `add-task` → `upload-image`

### D. 固定目标发散（goal-diverge）

提示词：`用 goal-skill 对本项目发散 goal projectId=… goalId=…`（可选 `runId=`）

1. `project-use`（有 `projectId`）
2. 解析 `goalId`（必填）；可用 `project-goal-get` / goals list 核对目标
3. `file-list` + `topic-list` 取事实与现有选题（不要虚构）
4. 若无 `runId`：`goal-diverge-trigger`（带 `goalId`）→ 得到 `runId`
5. **本地**按 Goal + 资料/选题生成 6～12 条 candidates（扁平 kind：`piece_*` / `topic` / `file_*` / `photo` / `template` / `speech` / `subgoal`）；**禁止**看 metrics、**禁止**调后端 generate
6. 写回前 `Read references/goal-diverge.md` 与 `references/artifact-kinds.md`
7. `goal-diverge-finish`（`run_id` + `candidates`）
8. 提示用户回 Web「候选菜单」勾选；采纳后的任务再用 A0 按族回写

**`subgoal` 推荐同时带菜单**：candidate 上加 `tasks: [...]`（同字段结构的非 subgoal 项）。finish 会同时创建 `pending_review` 目标 + 挂在其下的候选菜单。也可对已有待审目标直接 trigger/finish 写菜单（`goalId` 可为 `pending_review`）。

## 子能力与脚本

| 子能力 | 脚本 | 说明 |
|--------|------|------|
| `project-list` | `scripts/project-list.py` | 列出可管理项目 |
| `project-use` | `scripts/project-use.py` | 校验成员身份并缓存本地当前项目（不写服务端默认项目） |
| `project-goal-get` / `project-goal-update` | 对应脚本 | 读写大目标 |
| `goal-diverge-trigger` | `scripts/goal-diverge-trigger.py` | 创建 diverge_run |
| `goal-diverge-finish` | `scripts/goal-diverge-finish.py` | **回写候选**（Skill key） |
| `task-candidates-list` | `scripts/task-candidates-list.py` | 候选菜单列表 |
| `task-candidate-select` | `scripts/task-candidate-select.py` | 采纳/拒绝（可选；通常 Web） |
| `file-list` / `file-upsert` | 对应脚本 | 项目资料（`file_*` 任务回写） |
| `topic-list` / `topic-create` | 对应脚本 | 选题库（`topic` 任务回写） |
| `photo-create` | `scripts/photo-create.py` | 上传/入库项目图库 |
| `template-upsert` | `scripts/template-upsert.py` | 结构化建模板或链接导入 |
| `speech-create` | `scripts/speech-create.py` | 话术入库（`speech`：title + copies） |
| `speech-group-create` | `scripts/speech-group-create.py` | 创建话术分组 |
| `piece-group-create` | `scripts/piece-group-create.py` | 创建文案分组 |
| `content-task-list` | `scripts/content-task-list.py` | 项目任务列表 |
| `content-task-due` | `scripts/content-task-due.py` | **到期待执行任务**（仅无 taskId 时用） |
| `content-task-claim` | `scripts/content-task-claim.py` | **领取执行权 + batch_tag** |
| `content-task-finish` | `scripts/content-task-finish.py` | **结束本批**（piece 用 batch_tag；其它用 generated_count） |
| `content-task-create` | `scripts/content-task-create.py` | 创建任务（`output_type` 扁平 kind） |
| `content-task-get` | `scripts/content-task-get.py` | 任务详情（只读） |
| `piece-create` | `scripts/piece-create.py` | 保存成稿（`piece_*`） |
| `piece-list` / `piece-update` | 对应脚本 | 成稿列表/改稿 |
| `device-list` / `add-task` / … | 对应脚本 | 发布侧 |

### 已废弃

| 子能力 | 原因 |
|--------|------|
| `content-task-confirm` | 触发后端 LLM |

### `goal-diverge-trigger` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `projectId` | number | 是* | 项目；可缓存 |
| `goalId` | number | 是 | 已通过审核的目标 id |
| `trigger` | string | 否 | 默认 `manual` |

返回：`runId`、`info`（diverge_run 任务卡）。

### `goal-diverge-finish` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `run_id` / `runId` | number | 是 | diverge_run id |
| `candidates` | array | 是 | 见 [`references/goal-diverge.md`](references/goal-diverge.md) |

### `content-task-due` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `projectId` | number | 否 | 限定项目；省略则跨项目返回有权限的到期任务 |

### `content-task-claim` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `taskId` | number | 是 | 任务 ID |
| `trigger_source` | string | 否 | 默认 `agent` |

返回：`claimed`、`batch_tag`、`task`（含 topics / content_type_config）。

### `content-task-finish` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `taskId` | number | 是 | 任务 ID |
| `batch_tag` | string | 推荐 | 本批标签 |
| `failed` | bool | 否 | 强制标记失败 |
| `error` | string | 否 | 失败摘要 |

### `piece-create` 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `result` | string | 是 | 成稿全文 |
| `taskId` | number | 是* | 挂到已领取任务 |
| `topicId` | number | 是* | 选题 id |
| `content_type` | string | 否 | 默认 `xiaohongshu` |
| `batch_tag` | string | 推荐 | 与 claim 返回一致 |
| `batch_piece_index` | number | 推荐 | 该类型下从 1 起；幂等键 |

## 写稿提示（Agent）

1. 先 `file-list` / `content-task-get` 取事实，**不要虚构**价格、资质、案例。
2. 按启用类型的 `piece_count` 产出（新任务通常只有一种类型）；有选题则轮转均分。
3. **强制**：写每篇前打开 [`references/content-formats.md`](references/content-formats.md)，按该任务 `content_type` 小节写；格式以该文件为准（含共同规则）。
4. `piece_*` 的 `result` 必须是可直接复制到目标渠道的成品。`speech` 用 `title` + `copies[]`（每条 copy 可直接发出）；私聊场景每条 copy 为 3～5 行短消息（**单换行、禁止空行**），禁止 `【场景】` / `话术 A` / `转化要点`。
5. 同一批次所有 `piece-create` 使用相同 `batch_tag`。
6. 写完后必须 `content-task-finish`，否则 Web 一直显示执行中。

## 快速调用

```bash
export AIGOAL_API_KEY=sk-...

# Web 复制「执行任务 taskId=987 projectId=123」时：
python3 scripts/project-use.py '{"projectId":123}'
python3 scripts/content-task-get.py '{"taskId":987}'
python3 scripts/content-task-claim.py '{"taskId":987}'
# … 本地写稿 + piece-create …
python3 scripts/content-task-finish.py '{"taskId":987,"batch_tag":"..."}'

# 仅「拉取今日到期」时：
python3 scripts/content-task-due.py '{"projectId":123}'

# 固定目标发散：
python3 scripts/project-use.py '{"projectId":123}'
python3 scripts/project-goal-get.py '{"projectId":123}'
python3 scripts/file-list.py '{"projectId":123}'
python3 scripts/topic-list.py '{"projectId":123}'
python3 scripts/goal-diverge-trigger.py '{"projectId":123,"goalId":12,"trigger":"manual"}'
# … 本地生成 candidates …
python3 scripts/goal-diverge-finish.py '{"run_id":789,"candidates":[...]}'
```
