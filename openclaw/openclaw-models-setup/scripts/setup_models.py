import json
import os
import sys

def setup_models():
    filepath = os.path.expanduser('~/.openclaw/openclaw.json')
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        sys.exit(1)
        
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Setup Models in litellm provider
    litellm_models = data.setdefault('models', {}).setdefault('providers', {}).setdefault('litellm', {}).setdefault('models', [])
    litellm_model_ids = [m['id'] for m in litellm_models]

    # Model definitions
    models_to_add = {
        'deepseek-v4-pro': {'reasoning': True, 'vision': True, 'context': 195000},
        'deepseek-v3.2': {'reasoning': False},
        'deepseek-v3.2-think': {'reasoning': True},
        'kimi-k2.5': {'reasoning': False},
        'MiniMax-M2.5': {'reasoning': False},
        'glm-5': {'reasoning': False},
        'qwen3.5-plus': {'reasoning': False},
        'qwen3.6-plus': {'reasoning': False},
        'gemini/gemini-3.1-pro-preview': {'reasoning': True},
        'gemini/gemini-2.5-pro': {'reasoning': False},
        'gemini/gemini-2.5-flash-lite': {'reasoning': False},
        'gemini/gemini-2.5-flash': {'reasoning': False},
        'gemini/gemini-3-flash-preview': {'reasoning': False},
        'gemini/gemini-3.1-flash-lite-preview': {'reasoning': False}
    }

    for m_id, props in models_to_add.items():
        existing_model = next((m for m in litellm_models if m['id'] == m_id), None)
        if existing_model:
            if props.get('reasoning'):
                existing_model['reasoning'] = True
            # OpenClaw 0.x JSON schema may reject "vision" and "context" directly on the model level
            # We'll remove them or skip them to avoid "Unrecognized keys" errors.
            if 'vision' in existing_model:
                del existing_model['vision']
            if 'context' in existing_model:
                del existing_model['context']
        else:
            new_model = {
                'id': m_id,
                'name': m_id,
                'api': 'openai-completions'
            }
            if props.get('reasoning'):
                new_model['reasoning'] = True
            litellm_models.append(new_model)

    # Disable old litellm-google if exists
    if 'litellm-google' in data.get('models', {}).get('providers', {}):
        del data['models']['providers']['litellm-google']

    # 2. Setup Aliases
    defaults_models = data.setdefault('agents', {}).setdefault('defaults', {}).setdefault('models', {})
    aliases = {
        'litellm/deepseek-v4-pro': 'ds4p',
        'litellm/deepseek-v3.2': 'litellm-ds32',
        'litellm/deepseek-v3.2-think': 'litellm-ds32t',
        'litellm/kimi-k2.5': 'litellm-kimi25',
        'litellm/MiniMax-M2.5': 'litellm-mm25',
        'litellm/glm-5': 'litellm-glm5',
        'litellm/qwen3.5-plus': 'litellm-qwen35p',
        'litellm/qwen3.6-plus': 'litellm-qwen36p',
        'litellm/gemini/gemini-3.1-pro-preview': 'gemini-31p',
        'litellm/gemini/gemini-2.5-pro': 'gemini-25p',
        'litellm/gemini/gemini-2.5-flash-lite': 'gemini-25fl',
        'litellm/gemini/gemini-2.5-flash': 'gemini-25f',
        'litellm/gemini/gemini-3-flash-preview': 'gemini-3fp',
        'litellm/gemini/gemini-3.1-flash-lite-preview': 'gemini-31flp'
    }

    keys_to_delete = [k for k in defaults_models.keys() if k.startswith('litellm-google/') or k == 'litellm/deepseek-v4-pro']
    for k in keys_to_delete:
        del defaults_models[k]
        
    for model_path, alias in aliases.items():
        defaults_models[model_path] = {'alias': alias}

    # 3. Setup Agents List
    agent_list = data.setdefault('agents', {}).setdefault('list', [])
    
    # Remove old agent litellm-ds4pro if exists
    agent_list[:] = [a for a in agent_list if a.get('id') != 'litellm-ds4pro']
    
    agent_map = {a['id']: a for a in agent_list}

    agents_to_add = {
        'ds4p': ('LiteLLM DeepSeek V4 Pro', 'litellm/deepseek-v4-pro'),
        'litellm-ds32': ('LiteLLM DeepSeek V3.2', 'litellm/deepseek-v3.2'),
        'litellm-ds32t': ('LiteLLM DeepSeek V3.2 Think', 'litellm/deepseek-v3.2-think'),
        'litellm-kimi25': ('LiteLLM Kimi K2.5', 'litellm/kimi-k2.5'),
        'litellm-mm25': ('LiteLLM MiniMax M2.5', 'litellm/MiniMax-M2.5'),
        'litellm-glm5': ('LiteLLM GLM-5', 'litellm/glm-5'),
        'litellm-qwen35p': ('LiteLLM Qwen3.5 Plus', 'litellm/qwen3.5-plus'),
        'litellm-qwen36p': ('LiteLLM Qwen3.6 Plus', 'litellm/qwen3.6-plus'),
        'gemini-31p': ('Gemini 3.1 Pro Preview', 'litellm/gemini/gemini-3.1-pro-preview'),
        'gemini-25p': ('Gemini 2.5 Pro', 'litellm/gemini/gemini-2.5-pro'),
        'gemini-25fl': ('Gemini 2.5 Flash Lite', 'litellm/gemini/gemini-2.5-flash-lite'),
        'gemini-25f': ('Gemini 2.5 Flash', 'litellm/gemini/gemini-2.5-flash'),
        'gemini-3fp': ('Gemini 3 Flash Preview', 'litellm/gemini/gemini-3-flash-preview'),
        'gemini-31flp': ('Gemini 3.1 Flash Lite Preview', 'litellm/gemini/gemini-3.1-flash-lite-preview')
    }

    # First clean up any wrong refs
    for a in agent_list:
        if a.get('model', '').startswith('litellm-google/'):
            a['model'] = a['model'].replace('litellm-google/', 'litellm/')

    # Add missing agents
    for a_id, (a_name, a_model) in agents_to_add.items():
        if a_id in agent_map:
            if agent_map[a_id].get('model') != a_model:
                agent_map[a_id]['model'] = a_model
        else:
            agent_list.append({
                'id': a_id,
                'name': a_name,
                'workspace': f'C:/Users/junjun.zhao/.openclaw/workspace-{a_id}',
                'model': a_model
            })

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print('OpenClaw models, aliases, and agents successfully configured!')

if __name__ == '__main__':
    setup_models()
