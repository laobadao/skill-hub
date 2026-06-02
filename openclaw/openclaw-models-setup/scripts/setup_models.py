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
        'deepseek-v3.2': False,
        'deepseek-v3.2-think': True,
        'kimi-k2.5': False,
        'MiniMax-M2.5': False,
        'glm-5': False,
        'qwen3.5-plus': False,
        'qwen3.6-plus': False,
        'gemini/gemini-3.1-pro-preview': True,
        'gemini/gemini-2.5-pro': False,
        'gemini/gemini-2.5-flash-lite': False,
        'gemini/gemini-2.5-flash': False,
        'gemini/gemini-3-flash-preview': False,
        'gemini/gemini-3.1-flash-lite-preview': False
    }

    for m_id, reasoning in models_to_add.items():
        if m_id not in litellm_model_ids:
            new_model = {
                'id': m_id,
                'name': m_id,
                'api': 'openai-completions'
            }
            if reasoning:
                new_model['reasoning'] = True
            litellm_models.append(new_model)

    # Disable old litellm-google if exists
    if 'litellm-google' in data.get('models', {}).get('providers', {}):
        del data['models']['providers']['litellm-google']

    # 2. Setup Aliases
    defaults_models = data.setdefault('agents', {}).setdefault('defaults', {}).setdefault('models', {})
    aliases = {
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

    keys_to_delete = [k for k in defaults_models.keys() if k.startswith('litellm-google/')]
    for k in keys_to_delete:
        del defaults_models[k]
        
    for model_path, alias in aliases.items():
        defaults_models[model_path] = {'alias': alias}

    # 3. Setup Agents List
    agent_list = data.setdefault('agents', {}).setdefault('list', [])
    agent_map = {a['id']: a for a in agent_list}

    agents_to_add = {
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
