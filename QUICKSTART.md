# AgentGuard SDK - 快速开始

## 安装

```bash
pip install agentguard-zhx
```

## 使用（极简版）

```python
from agentguard import AgentGuardOpenAI

# 1. 初始化（一个客户端，所有功能）
client = AgentGuardOpenAI(
    agentguard_url="http://localhost:8080",
    agent_api_key="ag_xxx"
)

# 2. LLM 调用（完全兼容 OpenAI）
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)

# 3. 审批管理（集成功能）
status = client.approvals.get_status("approval_id")
client.approvals.submit_reason("approval_id", "reason")
```

## 就这么简单！

- ✅ 只需导入一个类
- ✅ 只需创建一个客户端
- ✅ 所有功能都在 `client` 上

## 详细文档

- [完整 README](README.md)
- [优化说明](UNIFIED_CLIENT_OPTIMIZATION.md)
- [最终方案](FINAL_UNIFIED_CLIENT.md)
- [优化总结](OPTIMIZATION_SUMMARY.md)
