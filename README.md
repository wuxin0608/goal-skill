# goal-skill

Cursor Agent Skill：内容项目运营（资料 / **Agent 本地按产物 kind 回写** / 选题 / **Goal 发散**）+ 小红书发布。

## 写稿原则

1. Web 派单；本地 Agent 按 `taskId=` / 今日 due 领取任务
2. `content-task-claim` → **按 `output_type` 族回写** → `content-task-finish`
3. 扁平 kind：`piece_*` / `file_*` / `topic` / `photo` / `template` / `subgoal`（见 `references/artifact-kinds.md`）
4. Goal 发散：candidates 使用扁平 kind → `goal-diverge-finish`
5. **禁止**使用 `content-task-confirm`（会触发服务端 LLM）；**禁止**根据赞藏改目标/选题

## 安装

### 方式一：Skills CLI（推荐）

```bash
npx skills add https://github.com/wuxin0608/goal-skill -g -y
```

### 方式二：手动克隆

```bash
git clone https://github.com/wuxin0608/goal-skill.git ~/.cursor/skills/goal-skill
```

## 配置

1. 在 Goal Web 端 **「AI Agent 接入」** 复制 `sk-...` API Key（**用户级固定密钥**，需 VIP）
2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 配置环境变量：

```bash
export AIGOAL_API_KEY=sk-your-key-here
# 可选：覆盖 API 地址
# export AIGOAL_API_BASE=https://ai2027.cn/goal/web
```

## 使用流程

```bash
# 选项目
python3 scripts/project-list.py
python3 scripts/project-use.py '{"projectId":123}'

# Web 复制「执行任务 taskId=987 projectId=123」时：
python3 scripts/content-task-get.py '{"taskId":987}'
python3 scripts/content-task-claim.py '{"taskId":987}'
# … 按 output_type 回写（piece → piece-create；file → file-upsert；…）…
python3 scripts/content-task-finish.py '{"taskId":987,"batch_tag":"..."}'
# 非 piece 例：
# python3 scripts/content-task-finish.py '{"taskId":987,"generated_count":3,"artifact_ids":[1,2,3]}'

# 固定目标发散
python3 scripts/goal-diverge-trigger.py '{"projectId":123,"goalId":12}'
# … 本地生成扁平 kind candidates（见 references/goal-diverge.md）…
python3 scripts/goal-diverge-finish.py '{"run_id":789,"candidates":[{"title":"…","output_type":"piece_xiaohongshu","prompt":"…"}]}'

# 资产回写示例
python3 scripts/photo-create.py '{"projectId":123,"file":"/tmp/a.png"}'
python3 scripts/template-upsert.py '{"projectId":123,"title":"对标A","content_type":"xiaohongshu"}'
```

详细参数见 [SKILL.md](./SKILL.md)。

## License

MIT
