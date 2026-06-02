# OpenClaw 自动化配置提示词 (Prompt)

您可以直接复制以下提示词发给 AI 助手，让其自动为您配置当前机器的 OpenClaw 环境：

---

请你帮我完成以下 OpenClaw 的模型环境配置任务:

1. 首先，请将 GitHub 上的技能仓库克隆到本地 (如果已存在请 pull 更新)。考虑到部分机器未配置 SSH Key，请优先使用 HTTPS 方式克隆：
   `git clone https://github.com/laobadao/skill-hub.git`
   (如果 HTTPS 报错，可备用尝试 `git clone git@github.com:laobadao/skill-hub.git`)

2. 在该仓库中，找到 OpenClaw 模型配置技能，路径应该在: 
   `skill-hub/openclaw/openclaw-models-setup/`

3. 请直接运行其中的自动配置脚本:
   `python skill-hub/openclaw/openclaw-models-setup/scripts/setup_models.py`
   执行脚本后，请确认 `~/.openclaw/openclaw.json` 中的模型、全局 aliases 映射以及 agent 列表已正确更新 (应包含 litellm 代理的 deepseek, kimi, glm, qwen 以及 gemini 等最新模型，以及诸如 ds4p, gemini-31p 等快捷别名)。

4. 配置完成后，请使用以下命令抽样���试网关是否连通 (要求响应时间必须小于1分钟):
   `openclaw agent --local --agent gemini-31p --message "测试模型是否正常工作,请回复:gemini-31p OK"`
   `openclaw agent --local --agent ds4p --message "测试模型是否正常工作,请回复:ds4p OK"`

请按步骤执行，并向我报告每一步的执行结果。
