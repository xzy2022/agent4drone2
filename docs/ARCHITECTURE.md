# Agent4Drone2 架构概述

本文档详细说明了 Agent4Drone2 的系统架构、设计原则和各模块之间的交互。

## 目录

- [设计原则](#设计原则)
- [架构层次](#架构层次)
- [模块详解](#模块详解)
- [数据流](#数据流)
- [单智能体 vs 多智能体](#单智能体-vs-多智能体)

## 设计原则

### 1. 模块化设计

每个模块都有单一的职责，清晰的接口定义：

- **api_client**: 只负责与 UAV API 通信
- **tools**: 只负责将 API 操作封装为 LangChain 工具
- **agents**: 只负责智能体逻辑和工作流编排
- **config**: 只负责配置管理
- **prompts**: 只负责提示词模板
- **state**: 只负责状态数据结构定义

### 2. 关注点分离

- **业务逻辑与基础设施分离**: 智能体决策逻辑与 API 通信分离
- **配置与代码分离**: LLM 配置独立于代码逻辑
- **接口与实现分离**: 提供向后兼容的适配器层

### 3. 可扩展性

- **易于添加新工具**: 工具注册表模式
- **支持多种 LLM**: 提供商抽象层
- **智能体可插拔**: 单智能体和多智能体可切换

## 架构层次

```
┌─────────────────────────────────────────────────────────────┐
│                     应用层 (Application)                      │
│                     main.py (GUI)                            │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                   适配器层 (Adapter)                          │
│              UAVControlAgent (legacy_adapter.py)             │
│          提供向后兼容接口，封装新架构的实现                    │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌──────▼─────────┐
│  单智能体模式   │  │   多智能体模式    │  │   配置管理      │
│ (UAVAgentGraph) │  │(MultiAgentCoord) │  │  (settings.py) │
└───────┬────────┘  └────────┬────────┘  └────────────────┘
        │                    │
        └────────┬───────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                    智能体层 (Agents)                         │
│  - ReAct Agent (LangChain)                                  │
│  - 专业化智能体 (Navigator, Reconnaissance, SafetyMonitor)  │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                    工具层 (Tools)                            │
│  UAVToolsRegistry - 管理 UAV 控制 LangChain 工具             │
│  - 信息获取工具 (list_drones, get_weather, etc.)             │
│  - 飞行控制工具 (take_off, move_to, land, etc.)              │
│  - 实用工具 (charge, calibrate, take_photo, etc.)            │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                  客户端层 (Client)                           │
│               UAVAPIClient (api_client/)                     │
│  - 封装所有 UAV API 端点                                      │
│  - 处理认证、错误处理、请求/响应                             │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                  UAV 控制系统 API                            │
│              (http://localhost:8000)                         │
└─────────────────────────────────────────────────────────────┘
```

## 模块详解

### 1. API 客户端模块 (`api_client/`)

**职责**: 与 UAV 控制系统 API 通信

**核心类**: `UAVAPIClient`

**功能**:
- 管理与 UAV API 的 HTTP 连接
- 处理认证 (API Key)
- 提供类型化的方法调用所有 API 端点
- 统一的错误处理

**主要方法类别**:
- **无人机操作**: `take_off()`, `land()`, `move_to()`, `rotate()`
- **会话操作**: `get_current_session()`, `get_task_progress()`
- **环境操作**: `get_weather()`, `get_targets()`, `get_obstacles()`
- **安全操作**: `check_point_collision()`, `check_path_collision()`

### 2. 工具模块 (`tools/`)

**职责**: 将 UAV API 操作封装为 LangChain 工具

**核心类**: `UAVToolsRegistry`

**设计模式**: 工具注册表模式

**工具分类**:
1. **信息获取工具**
   - `list_drones`: 列出所有无人机
   - `get_session_info`: 获取会话信息
   - `get_task_progress`: 获取任务进度
   - `get_weather`: 获取天气状况
   - `get_drone_status`: 获取无人机状态
   - `get_nearby_entities`: 获取附近实体

2. **飞行控制工具**
   - `take_off`: 起飞
   - `land`: 降落
   - `move_to`: 移动到指定坐标
   - `move_towards`: 沿方向移动
   - `change_altitude`: 改变高度
   - `hover`: 悬停
   - `rotate`: 旋转
   - `return_home`: 返回起始点

3. **实用工具**
   - `set_home`: 设置起始点
   - `calibrate`: 校准传感器
   - `take_photo`: 拍照
   - `charge`: 充电

4. **通信工具**
   - `send_message`: 发送消息给其他无人机
   - `broadcast`: 广播消息

**JSON 参数规范**: 所有工具统一使用 JSON 字符串作为输入，确保一致性

### 3. 状态模块 (`state/`)

**职责**: 定义智能体工作流的状态结构

**核心类**:
- `UAVAgentState`: 单智能体状态
- `MultiAgentState`: 多智能体状态

**状态字段**:
```python
# UAVAgentState
{
    "messages": [],              # 用户与智能体之间的消息
    "session_info": {},          # 会话信息
    "task_progress": {},         # 任务进度
    "drones_status": [],         # 无人机状态
    "intermediate_steps": [],    # 中间步骤
    "current_step": 0,           # 当前步骤
    "max_iterations": 50,        # 最大迭代次数
    "final_answer": None,        # 最终答案
    "error": None                # 错误信息
}

# MultiAgentState
{
    "messages": [],
    "active_agents": [],         # 活跃智能体列表
    "agent_roles": {},           # 智能体角色映射
    "task_queue": [],            # 待执行任务队列
    "completed_tasks": [],       # 已完成任务
    "agent_results": {},         # 各智能体结果
    "shared_context": {},        # 共享上下文
    "current_phase": "",         # 当前阶段
    "final_plan": None,          # 最终计划
    "final_answer": None,
    "error": None
}
```

### 4. 提示词模块 (`prompts/`)

**职责**: 管理智能体的系统提示词和模板

**核心内容**:
- `UAV_AGENT_SYSTEM_PROMPT`: 单智能体系统提示词
- `COORDINATOR_SYSTEM_PROMPT`: 协调器提示词
- 专业化智能体提示词（导航员、侦察专家、安全监控员）
- 错误处理模板

**提示词要素**:
- 角色定义
- 安全规则
- 响应格式规范
- Action Input 格式规则
- 工具使用示例

### 5. 智能体模块 (`agents/`)

#### 5.1 单智能体 (`agents/single/`)

**核心类**: `UAVAgentGraph`

**实现方式**: 使用 LangChain 的 ReAct Agent

**工作流程**:
1. 接收用户命令
2. 使用 React 模式: Thought → Action → Action Input → Observation
3. 迭代执行直到完成任务或达到最大迭代次数
4. 返回最终答案

**关键方法**:
- `execute(command)`: 执行自然语言命令
- `run_interactive()`: 交互式运行模式
- `refresh_session_context()`: 刷新会话上下文
- `get_session_summary()`: 获取会话摘要

#### 5.2 多智能体 (`agents/multi/`)

**核心类**: `MultiAgentCoordinator`

**专业化智能体**:

1. **NavigatorAgent (导航员)**
   - 路径规划
   - 移动执行
   - 障碍物规避
   - 电池效率优化

2. **ReconnaissanceAgent (侦察专家)**
   - 目标识别
   - 拍照操作
   - 目标访问跟踪
   - 侦察结果报告

3. **SafetyMonitorAgent (安全监控员)**
   - 电池监控
   - 天气检查
   - 碰撞检测
   - 安全告警

**协调流程**:
```
用户命令
    ↓
任务分解 (_decompose_task)
    ↓
计划生成
    ↓
任务执行 (_execute_plan)
    ↓
结果聚合 (_aggregate_results)
    ↓
最终答案
```

#### 5.3 遗留适配器 (`agents/legacy_adapter.py`)

**核心类**: `UAVControlAgent`

**目的**: 提供向后兼容接口

**作用**:
- 保持与旧 `uav_agent.py` 相同的接口
- 内部使用新的 `UAVAgentGraph` 实现
- 使现有 GUI 代码 (main.py) 无需修改即可工作

### 6. 配置模块 (`config/`)

**核心类**: `LLMProviderConfig`

**支持的提供商**:
- **Ollama**: 本地 LLM，无需 API Key
- **OpenAI**: 云端 LLM，需要 API Key
- **OpenAI-Compatible**: 兼容 API 的第三方服务

**配置加载**:
- 从 `llm_settings.json` 加载
- 环境变量支持
- 命令行参数覆盖

## 数据流

### 单智能体模式数据流

```
用户输入
    ↓
UAVControlAgent.execute()
    ↓
UAVAgentGraph.execute()
    ↓
AgentExecutor.invoke()
    ↓
ReAct 循环:
    ├─ LLM 推理 (Thought)
    ├─ 选择工具 (Action)
    ├─ 执行工具 (Action Input)
    └─ 获取结果 (Observation)
    ↓
UAVAPIClient (如果工具需要 API 调用)
    ↓
UAV 控制系统 API
    ↓
返回结果
    ↓
格式化输出
```

### 多智能体模式数据流

```
用户输入
    ↓
MultiAgentCoordinator.execute()
    ↓
任务分解
    ├─ 分析命令
    ├─ 确定需要的智能体
    └─ 生成执行计划
    ↓
执行计划
    ├─ NavigatorAgent (导航任务)
    ├─ ReconnaissanceAgent (侦察任务)
    └─ SafetyMonitorAgent (安全检查)
    ↓
结果聚合
    ├─ 收集各智能体结果
    ├─ 合并输出
    └─ 生成最终答案
    ↓
返回结果
```

## 单智能体 vs 多智能体

### 单智能体模式

**适用场景**:
- 简单任务
- 单无人机操作
- 快速响应需求
- 资源受限环境

**优点**:
- 实现简单
- 响应快速
- 资源占用少
- 易于调试

**缺点**:
- 单点故障
- 无并行处理
- 复杂任务可能需要更多迭代

### 多智能体模式

**适用场景**:
- 复杂任务
- 多无人机协调
- 需要专业化处理
- 任务可分解

**优点**:
- 任务并行
- 专业化分工
- 更好的可扩展性
- 提高系统鲁棒性

**缺点**:
- 更复杂
- 资源占用更多
- 协调开销

## 技术栈

- **LangChain**: 智能体框架
- **LangGraph**: 状态管理（预留）
- **Requests**: HTTP 客户端
- **Python 3.8+**: 编程语言

## 未来改进

- [ ] 使用 LangGraph 实现真正的状态图工作流
- [ ] 添加智能体之间的通信机制
- [ ] 实现更智能的任务分解算法
- [ ] 添加持久化状态存储
- [ ] 实现智能体学习和优化
