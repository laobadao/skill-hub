# Paper| EAGLE-3 深入详解

> 论文链接: https://huggingface.co/papers/2503.01840  
> GitHub: https://github.com/SafeAILab/EAGLE

---

## 论文核心创新点深入解读

### 核心问题：EAGLE-2 的瓶颈

EAGLE-2 虽然已经实现了较好的加速效果，但存在两个关键瓶颈：

#### 问题 1: Feature Prediction 约束

```plaintext
EAGLE-2 流程:
    Feature(t) → Draft Model → Feature(t+1) → LM Head → Token(t+1)

问题:
    1. 需要预测 Feature，再转 Token
    2. Feature Prediction Loss 约束了模型表达能力
    3. 增加 Training Data 无法有效提升性能
```

**论文实验数据:**

| Training Data Scale | EAGLE-2 Speedup | EAGLE-2 Accept Length |
|---------------------|-----------------|----------------------|
| 1x | 3.2x | 4.0 |
| 2x | 3.3x | 4.1 |
| 4x | 3.4x | 4.2 |
| 8x | 3.5x | 4.3 |

**结论:** 训练数据增加 8 倍，加速效果仅提升 ~10%

#### 问题 2: 仅使用 Top-Layer Feature

```plaintext
EAGLE-2 只使用顶层特征:
    h_top = Target Model Layer[-1] output

局限性:
    1. 顶层特征主要编码 "下一个 token" 信息
    2. 对 "下下个 token" 预测能力有限
    3. 多步 Draft 时接受率快速下降
```

**论文实验数据 (Acceptance Rate):**

| Draft Step | 0-α (第1个) | 1-α (第2个) | 2-α (第3个) |
|------------|-------------|-------------|-------------|
| EAGLE-2 | 0.78 | 0.55 | 0.35 |
| EAGLE (no fea pred) | 0.82 | 0.25 | 0.10 |
| **EAGLE-3** | **0.80** | **0.65** | **0.52** |

---

## EAGLE-3 核心创新: Training-Time Test

### 技术原理

```plaintext
传统 Training:
    Training: f₁, f₂, ..., fₜ → Draft Model → âₜ₊₁
    Test:     f₁, f₂, ..., fₜ → Draft Model → âₜ₊₁
    
问题: Training 时用 Ground-Truth fₜ₊₁，但 Test 时用预测值 âₜ₊₁
      → 分布不一致，多步预测性能差

Training-Time Test:
    Training Step 1: f₁, ..., fₜ → Draft Model → âₜ₊₁
    Training Step 2: f₁, ..., fₜ, âₜ₊₁ → Draft Model → âₜ₊₂
                     ↑ 使用 Step 1 的预测值，而非 Ground-Truth
    
    Test: 与 Training 完全一致
```

### 数学公式

**EAGLE-2 Loss:**
```plaintext
L = L_fea + L_token
  = ||f̂ₜ₊₁ - fₜ₊₁||² + CrossEntropy(lm_head(f̂ₜ₊₁), tₜ₊₁)
```

**EAGLE-3 Loss:**
```plaintext
L = L_token only
  = CrossEntropy(lm_head(âₜ₊₁), tₜ₊₁)
  
其中 âₜ₊₁ = Draft Model(concat(l, m, h), t₁...tₜ)
```

---

## 多层特征融合机制

### 三层特征定义

| 特征 | 符号 | 来源层 | 信息类型 |
|------|------|--------|----------|
| **Low-level** | l | Layer 2 | 词法、句法信息 |
| **Mid-level** | m | Layer 18 | 语义组合、关系 |
| **High-level** | h | Layer 33 | 推理、上下文理解 |

### 融合流程

```plaintext
Target Model Forward:
    │
    ├── Layer 2:   l = [B, L, k]     (k = hidden_size)
    ├── Layer 18:  m = [B, L, k]
    └── Layer 33:  h = [B, L, k]
    │
    ▼
Concat: [l, m, h] → [B, L, 3k]
    │
    ▼
FC Layer: Linear(3k → k)
    │
    ▼
g = [B, L, k]  (融合后的特征)
    │
    ▼
Draft Model Input
```

### 实验验证 (Ablation Study)

| 特征组合 | MT-Bench Score | Speedup |
|----------|----------------|---------|
| h only (EAGLE-2) | 8.12 | 3.2x |
| l + h | 8.15 | 3.8x |
| m + h | 8.18 | 4.0x |
| l + m + h (EAGLE-3) | **8.22** | **4.4x** |

---

## 实验结果深入分析

### 速度提升对比

| Target Model | Method | Speedup | Accept Length |
|--------------|--------|---------|---------------|
| **Vicuna 13B** | Vanilla | 1.0x | - |
| | Speculative (68M) | 1.9x | 2.1 |
| | Medusa | 2.1x | 2.5 |
| | EAGLE | 3.1x | 3.8 |
| | EAGLE-2 | 4.1x | 4.5 |
| | **EAGLE-3** | **5.6x** | **6.2** |
| **LLaMA-3.1 8B** | EAGLE-2 | 3.2x | 4.0 |
| | **EAGLE-3** | **4.4x** | **5.5** |
| **LLaMA-3.3 70B** | EAGLE-2 | 2.8x | 3.2 |
| | **EAGLE-3** | **4.1x** | **5.0** |

### Scaling Law 发现

| Training Data | EAGLE-2 Speedup | EAGLE-3 Speedup | EAGLE-3 Accept Length |
|---------------|-----------------|-----------------|----------------------|
| 1x (ShareGPT) | 3.2x | 3.6x | 4.0 |
| 2x | 3.3x | 4.0x | 4.5 |
| 4x | 3.4x | 4.3x | 5.2 |
| 8x | 3.5x | **4.4x** | **5.5** |

**关键发现:**
- EAGLE-2: 数据增加 8 倍 → 性能提升 ~10%
- EAGLE-3: 数据增加 8 倍 → 性能提升 ~22%
- **EAGLE-3 展现出线性 Scaling Law**

### SGLang 框架集成

**测试环境:**
- 模型: LLaMA-3.1 8B
- 硬件: NVIDIA H100
- Batch Size: 64

| Metric | Vanilla | EAGLE-2 | EAGLE-3 |
|--------|---------|---------|---------|
| Throughput (tokens/s) | 158.34 | 244.10 | **373.25** |
| Speedup | 1.0x | 1.54x | **2.36x** |

**关键结论:**
- 即使在 Batch Size=64 的大吞吐场景，EAGLE-3 仍能提升 38% 吞吐量
- 打破了 "投机采样会降低大 Batch 吞吐" 的传统认知

---

## 树状验证 vs 链式验证

### 核心差异

| 维度 | 链式验证 | 树状验证 |
|------|----------|----------|
| **Draft 结构** | 单条链：t₁ → t₂ → t₃ → ... | 树状：每个节点可以有多条分支 |
| **验证方式** | 逐个验证，遇到拒绝就停止 | 并行验证整棵树，选择最长接受路径 |
| **复杂度** | O(n) 顺序验证 | O(n) 并行验证（但需要树结构管理） |
| **接受率** | 低 | **高 20-40%** |
| **加速比** | 3-4x | **4-6x** |

### SGLang vs vLLM 实现

| 特性 | vLLM | SGLang |
|------|------|--------|
| **默认验证方式** | 链式 | 树状（EAGLE 模式） |
| **树采样支持** | ❌ 不支持 | ✅ 支持 |
| **并行验证** | 部分 | 完全支持 |
| **EAGLE-3 集成** | 需要额外配置 | 原生支持 |

---

## EAGLE-3 树状验证关键参数

```bash
--speculative-num-steps 6       # Draft Model 连续生成的步数（树的深度）
--speculative-eagle-topk 10     # 每个节点保留的候选分支数（树的宽度）
--speculative-num-draft-tokens 32  # 总候选 token 数量上限
```

### 调参建议

| 场景 | num_steps | topk | num_draft_tokens |
|------|-----------|------|------------------|
| **低延迟（单请求）** | 6-8 | 4-6 | 32 |
| **高吞吐（大 batch）** | 4-6 | 8-10 | 64 |
| **内存受限** | 4 | 4 | 16 |

---

## 代码实现关键点

### SGLang 中的三层捕获

```python
# python/sglang/srt/models/qwen3.py: 588-601
def set_eagle3_layers_to_capture(self, layer_ids=None):
    if layer_ids is None:
        num_layers = self.config.num_hidden_layers
        self.model.layers_to_capture = [
            2,              # Low-level
            num_layers // 2,  # Mid-level
            num_layers - 3,   # High-level
        ]
```

### 三层特征融合

```python
# python/sglang/srt/models/llama_eagle3.py
def forward(self, input_ids, positions, forward_batch, ...):
    # 获取三层特征
    hidden_states = forward_batch.spec_info.hidden_states
    # Shape: [B, L, 3*k] = [B, L, 12288]
    
    # FC 降维
    if hidden_states.shape[-1] != embeds.shape[-1]:
        hidden_states = self.fc(hidden_states)
    # Shape: [B, L, k] = [B, L, 4096]
    
    # 与 embedding 拼接
    hidden_states = torch.cat([embeds, hidden_states], dim=-1)
    # Shape: [B, L, 2*k] = [B, L, 8192]
```

---

## 实践建议

### 训练 EAGLE-3 Draft Model

1. **数据准备**
   - 使用 ShareGPT 或类似对话数据
   - 数据量建议 8x ShareGPT 以上

2. **特征提取**
   - 修改目标模型，导出 Layer 2, 18, 33 的特征
   - 保存为训练数据格式

3. **Training-Time Test**
   - 实现 Step 1 → Step 2 的级联训练
   - 使用前一步的预测值作为下一步输入

### 推理部署

```bash
python -m sglang.launch_server \
    --model /path/to/target_model \
    --speculative-algorithm EAGLE3 \
    --speculative-draft-model-path /path/to/draft_model \
    --speculative-num-steps 6 \
    --speculative-eagle-topk 10 \
    --speculative-num-draft-tokens 32
```

---

## 关键 Q&A

### Q1: 为什么用 "can" 的隐状态而不是 "I" 的？

**核心理解：Target Model 预测 "I" 时，"I" 还不存在**

| 阶段 | 已输入 Target Model | 已有隐状态 | 预测 |
|------|---------------------|------------|------|
| Prefill | "How can" | "How", "can" | "I" |
| Decode 1 | "How can I" | "How", "can", "I" | "do" |
| Decode 2 | "How can I do" | "How", "can", "I", "do" | "it" |

**答案：** 预测 token 时用的是**前一个 token 的隐状态**，因为预测的 token 还没被输入模型。

### Q2: 为什么 Draft Model 用 embed("can") 而不是 embed("I")？

**答案：** Draft Model 是独立预测，需要从已知 token 开始。"can" 是最后一个**已知** token，"I" 是预测结果，不是已知输入。

### Q3: vLLM 是否支持树状验证？

**答案：** 不支持。vLLM 只支持链式验证。需要树状验证 → 使用 SGLang。

### Q4: Batch Size=64 下提升 38% 归功于什么？

**答案：** EAGLE-3 + SGLang 树状验证的组合。vLLM + EAGLE-3 预估只有 10-15% 提升。

---

## 总结

EAGLE-3 是大模型推理加速技术的重要升级：

| 维度 | EAGLE-2 | EAGLE-3 | 提升 |
|------|---------|---------|------|
| **Speedup (LLaMA-3.1 8B)** | 3.2x | 4.4x | +37% |
| **Accept Length** | 4.0 | 5.5 | +37% |
| **训练数据利用率** | 低 | 高 | 线性提升 |
| **大 Batch 吞吐** | 可能下降 | 提升 38% | 显著改善 |

**核心创新：**
1. **直接生成 token**（放弃特征预测约束）
2. **多层特征融合**（低层 + 中层 + 高层）
3. **Training-Time Test**（训练时模拟推理行为）

**建议：**
- 追求简单：用 vLLM 链式验证（2-3x）
- 追求性能：用 SGLang + EAGLE-3 树状验证（5-6x）
