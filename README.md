# Skill Hub

AI 技能文档知识库，按分类组织。

## 目录结构

```
skill-hub/
├── ai/                    # 通用 AI 技术（prompt engineering, RAG 等）
├── agent/                 # Agent 开发（多智能体、工具调用等）
├── claude/                # Claude 相关（Claude Code, MCP 等）
├── cursor/                # Cursor 编辑器技巧
├── openclaw/              # OpenClaw 平台（技能、插件、配置）
├── quant/                 # 量化推理加速（vLLM, SGLang, 量化技术）
└── papers/                # 论文笔记（LLM、推理加速等）
```

## 文档列表

### Papers (论文笔记)

- [EAGLE-3 Speculative Decoding](papers/eagle-3-speculative-decoding.md) - LLM 推理加速的突破性方法，最高 6.5x 加速

## 分类说明

| 分类 | 内容示例 |
|------|----------|
| `ai/` | Prompt engineering, RAG, Fine-tuning, Evaluation |
| `agent/` | Multi-agent, Tool calling, Function calling, LangChain |
| `claude/` | Claude Code, MCP server, Anthropic API |
| `cursor/` | Cursor rules, .cursorignore, AI pair programming |
| `openclaw/` | Skills, plugins, openclaw.json, gateway config |
| `quant/` | vLLM, SGLang, TensorRT-LLM, AWQ, GPTQ, speculative decoding |
| `papers/` | LLM 论文笔记，如 EAGLE-3、FlashAttention 等 |

## 贡献

欢迎提交 PR 添加新的技能文档！

## License

MIT
