# Agent4Drone2 文档

这是重构后的 Agent4Drone2 项目文档 - 一个基于 LLM 智能体的无人机控制系统。

## 目录

- [项目概述](#项目概述)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [文档索引](#文档索引)

## 项目概述

Agent4Drone2 是一个模块化的、基于智能体的无人机控制系统，支持使用自然语言命令控制无人机。系统使用 LangChain 进行智能体编排，同时支持单智能体和多智能体工作流。

### 核心特性

- **自然语言控制**：使用简单的英文命令控制无人机
- **模块化架构**：清晰的关注点分离，各模块职责明确
- **单智能体模式**：使用单一智能代理进行简单、专注的无人机控制
- **多智能体模式**：使用专业化智能体（导航员、侦察专家、安全监控员）进行协调控制
- **多 LLM 提供商支持**：支持 Ollama、OpenAI 和 OpenAI 兼容 API
- **基于工具的架构**：使用 LangChain 工具实现安全可靠的无人机操作
- **向后兼容**：现有代码可继续使用新架构

## 项目结构

```
src/
├── __init__.py
├── agents/              # 智能体实现
│   ├── __init__.py
│   ├── legacy_adapter.py    # 向后兼容层
│   ├── single/              # 单智能体工作流
│   │   ├── __init__.py
│   │   └── uav_agent.py
│   └── multi/               # 多智能体协调
│       ├── __init__.py
│       ├── specialized_agents.py
│       └── coordinator.py
├── api_client/          # UAV API 客户端
│   ├── __init__.py
│   └── client.py
├── config/              # 配置管理
│   ├── __init__.py
│   └── settings.py
├── prompts/             # 智能体提示词
│   ├── __init__.py
│   └── agent_prompts.py
├── state/               # 状态定义
│   ├── __init__.py
│   └── agent_state.py
├── tools/               # LangChain 工具
│   ├── __init__.py
│   └── uav_tools.py
└── utils/               # 工具函数
    └── __init__.py
```

### 模块说明

| 模块 | 描述 |
|------|------|
| `agents/` | 单智能体和多智能体工作流的实现 |
| `api_client/` | UAV 控制系统的 HTTP API 客户端 |
| `config/` | LLM 提供商和设置的配置管理 |
| `prompts/` | 不同类型智能体的系统提示词 |
| `state/` | LangGraph 工作流的 TypedDict 状态定义 |
| `tools/` | 封装 UAV API 操作的 LangChain 工具 |
| `utils/` | 工具函数和辅助方法 |

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本用法

#### 使用遗留适配器（推荐用于现有代码）

```python
from src.agents import UAVControlAgent

# 初始化智能体
agent = UAVControlAgent(
    base_url="http://localhost:8000",
    llm_provider="ollama",
    llm_model="llama2"
)

# 执行命令
result = agent.execute("将第一架无人机起飞至15米高度")
print(result['output'])
```

#### 直接使用新架构

```python
from src.api_client import UAVAPIClient
from src.agents.single import UAVAgentGraph

# 创建 API 客户端
client = UAVAPIClient(base_url="http://localhost:8000")

# 创建单智能体
agent = UAVAgentGraph(
    client=client,
    llm_provider="ollama",
    llm_model="llama2"
)

# 执行命令
result = agent.execute("列出所有可用的无人机")
```

#### 使用多智能体模式

```python
from src.api_client import UAVAPIClient
from src.agents.multi import MultiAgentCoordinator

# 创建具有专业化智能体的协调器
coordinator = MultiAgentCoordinator(
    client=UAVAPIClient(),
    llm_provider="openai",
    llm_model="gpt-4o-mini"
)

# 执行命令（将委托给相应的智能体）
result = coordinator.execute("侦察所有目标并拍照")
```

## 文档索引

- [架构概述](ARCHITECTURE.md) - 详细的系统架构说明
- [API 参考](API_REFERENCE.md) - 完整的 API 文档
- [使用指南](USAGE_GUIDE.md) - 详细的使用示例和模式
- [迁移指南](MIGRATION.md) - 从旧代码库迁移的指南

## 许可证

本项目采用 MIT 许可证。
