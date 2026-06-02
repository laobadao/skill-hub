---
name: openclaw-models-setup
description: Automatically configures OpenClaw with D-Robotics LiteLLM gateway models including DeepSeek, Kimi, GLM, Qwen, and Gemini. Use when asked to setup models on another machine or configure OpenClaw models.
---

# OpenClaw Models Setup

This skill configures an OpenClaw instance to use the D-Robotics LiteLLM gateway, adding standard models (DeepSeek, Kimi, GLM, Qwen) and Gemini models with proper alias mappings and agent definitions.

## What this configures:

1. Adds all models under the `litellm` provider with `openai-completions` API format
2. Special handling for Gemini: uses `gemini/` prefix for ID and name
3. Configures global short aliases in `agents.defaults.models`
4. Creates dedicated Agent entries in `agents.list`

## Workflow

### 1. Execute Setup Script

Run the bundled python script to automatically patch the `~/.openclaw/openclaw.json` file:

```bash
python scripts/setup_models.py
```

### 2. Verify Provider Credentials

Ensure the target machine's `~/.openclaw/openclaw.json` has the correct credentials for the `litellm` provider:

```json
"litellm": {
  "baseUrl": "https://llmgateway.d-robotics.cc/v1",
  "apiKey": "<API_KEY>"
}
```

### 3. Verification Test

Run a quick local agent test to ensure the models resolve correctly and don't timeout (should respond within a few seconds, limit is 1 minute):

```bash
openclaw agent --local --agent gemini-31p --message "测试模型是否正常工作，请回复: gemini-31p OK"
openclaw agent --local --agent litellm-ds32t --message "测试模型是否正常工作，请回复: ds32t OK"
```