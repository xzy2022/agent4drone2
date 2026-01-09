# Agent4Drone2 使用指南

本文档提供 Agent4Drone2 的详细使用说明和实用示例。

## 目录

- [环境准备](#环境准备)
- [基础配置](#基础配置)
- [使用模式](#使用模式)
- [命令示例](#命令示例)
- [高级用法](#高级用法)
- [故障排除](#故障排除)

---

## 环境准备

### 1. 安装依赖

```bash
pip install langchain langchain-openai langchain-ollama langchain-classic requests
```

### 2. 启动 UAV API 服务器

确保 UAV 控制系统 API 服务器正在运行：

```bash
# 假设 API 服务器在 localhost:8000
# 根据实际情况调整
```

### 3. 配置 LLM 提供商

#### 使用 Ollama（推荐用于本地测试）

```bash
# 安装 Ollama
# 访问 https://ollama.ai/

# 拉取模型
ollama pull llama2

# 启动 Ollama 服务
ollama serve
```

#### 使用 OpenAI

```bash
# 设置环境变量
export OPENAI_API_KEY="your-api-key-here"

# 或在代码中提供
```

---

## 基础配置

### 方法 1: 使用 llm_settings.json

创建 `llm_settings.json` 文件：

```json
{
  "provider_configs": {
    "Ollama": {
      "type": "ollama",
      "base_url": "http://localhost:11434",
      "default_model": "llama2",
      "default_models": [],
      "requires_api_key": false
    },
    "OpenAI": {
      "type": "openai-compatible",
      "base_url": "https://api.openai.com/v1",
      "default_model": "gpt-4o-mini",
      "default_models": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
      "requires_api_key": true,
      "api_key": "your-api-key-here"
    }
  },
  "selected_provider": "Ollama"
}
```

### 方法 2: 使用环境变量

```bash
# OpenAI API Key
export OPENAI_API_KEY="your-key"

# UAV API Key
export UAV_API_KEY="your-uav-key"

# LLM API Key（通用）
export LLM_API_KEY="your-key"
```

---

## 使用模式

### 模式 1: 使用向后兼容接口（推荐）

这是最简单的方式，与现有代码兼容。

```python
from src.agents import UAVControlAgent

# 初始化
agent = UAVControlAgent(
    base_url="http://localhost:8000",
    llm_provider="ollama",
    llm_model="llama2",
    verbose=True
)

# 执行命令
result = agent.execute("列出所有可用的无人机")
print(result['output'])

# 检查结果
if result['success']:
    print("成功:", result['output'])
else:
    print("失败:", result['output'])
```

### 模式 2: 直接使用新架构

```python
from src.api_client import UAVAPIClient
from src.agents.single import UAVAgentGraph

# 创建客户端
client = UAVAPIClient(
    base_url="http://localhost:8000",
    api_key=None  # 可选
)

# 创建智能体
agent = UAVAgentGraph(
    client=client,
    llm_provider="ollama",
    llm_model="llama2",
    temperature=0.1,
    verbose=True
)

# 执行命令
result = agent.execute("将第一架无人机起飞到20米")
```

### 模式 3: 多智能体协调

```python
from src.api_client import UAVAPIClient
from src.agents.multi import MultiAgentCoordinator

# 创建协调器
coordinator = MultiAgentCoordinator(
    client=UAVAPIClient(),
    llm_provider="openai",
    llm_model="gpt-4o-mini",
    verbose=True
)

# 执行复杂任务
result = coordinator.execute("侦察所有目标位置并拍照")

# 结果会包含执行计划
print("执行计划:", result['plan'])
print("最终输出:", result['output'])
```

### 模式 4: 交互式命令行

```python
from src.agents import UAVControlAgent

agent = UAVControlAgent()
agent.run_interactive()
```

**交互式命令**:
- `quit`, `exit`, `q`: 退出
- `status`: 显示会话摘要
- `help`: 显示示例命令
- 任何自然语言命令

---

## 命令示例

### 信息查询

#### 查看所有无人机

```
列出所有可用的无人机
有哪些无人机可用？
显示所有无人机的状态
```

#### 查看会话信息

```
显示当前任务信息
任务的目标是什么？
查看任务进度
```

#### 查看环境

```
检查天气状况
查看所有目标
有哪些障碍物？
查看 drone-001 附近有什么
```

#### 查看特定无人机状态

```
显示 drone-001 的状态
drone-001 的电池还剩多少？
```

### 基本控制

#### 起飞

```
将 drone-001 起飞到 15 米
Take off drone-001 to 20 meters altitude
```

#### 降落

```
让 drone-001 降落
Land drone-001
```

#### 移动到坐标

```
将 drone-001 移动到坐标 (100, 50, 20)
Move drone-001 to x=100, y=50, z=20
```

#### 改变高度

```
将 drone-001 的高度改为 30 米
Change altitude of drone-001 to 25 meters
```

#### 悬停

```
让 drone-001 悬停 5 秒
Hover drone-001 for 10 seconds
```

#### 旋转

```
将 drone-001 旋转面向东方（90度）
Rotate drone-001 to heading 180
```

#### 返回起始点

```
让 drone-001 返回起始点
Return drone-001 home
```

### 任务执行

#### 访问所有目标

```
访问所有目标点
使用第一架无人机访问所有目标
完成所有目标的侦察
```

#### 拍照

```
在所有目标位置拍照
让 drone-001 拍照
在当前位置拍照
```

#### 巡逻

```
巡逻指定区域
搜索区域内的所有目标
```

### 安全操作

#### 检查碰撞

```
检查 (0,0,10) 到 (100,100,10) 之间是否有障碍物
从当前位置移动到目标是否安全
```

#### 电池管理

```
检查所有无人机的电池状态
为低电量的无人机充电
让 drone-001 充电 30%
```

### 通信

#### 发送消息

```
从 drone-001 发送消息 "Hello" 给 drone-002
```

#### 广播

```
让 drone-001 广播 "Warning"
```

### 组合任务

```
1. 起飞到 20 米，然后访问所有目标，最后返回
2. 检查天气，然后起飞，访问所有目标并拍照
3. 使用所有可用无人机完成任务，确保安全
```

---

## 高级用法

### 自定义 LLM 配置

#### 使用自定义 OpenAI 兼容 API

```python
from src.agents import UAVControlAgent

agent = UAVControlAgent(
    base_url="http://localhost:8000",
    llm_provider="openai-compatible",
    llm_model="your-custom-model",
    llm_base_url="https://your-api-endpoint.com/v1",
    llm_api_key="your-api-key"
)
```

#### 调整温度参数

```python
# 更确定性的输出（推荐）
agent = UAVControlAgent(llm_temperature=0.1)

# 更创造性的输出
agent = UAVControlAgent(llm_temperature=0.7)
```

### 使用专业化智能体

#### 仅使用导航员

```python
from src.agents.multi import NavigatorAgent
from src.api_client import UAVAPIClient
from langchain_ollama import ChatOllama

client = UAVAPIClient()
llm = ChatOllama(model="llama2")

navigator = NavigatorAgent(client, llm, verbose=True)
result = navigator.execute({
    'command': '将无人机移动到 (100, 50, 20)'
})
```

#### 仅使用侦察专家

```python
from src.agents.multi import ReconnaissanceAgent

recon = ReconnaissanceAgent(client, llm, verbose=True)
result = recon.execute({
    'command': '在所有目标位置拍照'
})
```

#### 仅使用安全监控员

```python
from src.agents.multi import SafetyMonitorAgent

safety = SafetyMonitorAgent(client, llm, verbose=True)
result = safety.execute({
    'command': '检查所有无人机的安全状态'
})
```

### 直接使用工具

```python
from src.api_client import UAVAPIClient
from src.tools import UAVToolsRegistry

client = UAVAPIClient()
registry = UAVToolsRegistry(client)

# 获取特定工具
take_off_tool = registry.get_tool('take_off')

# 直接调用工具
result = take_off_tool.run('{"drone_id": "drone-001", "altitude": 15.0}')
```

### 获取会话信息

```python
from src.agents import UAVControlAgent

agent = UAVControlAgent()

# 获取会话摘要
summary = agent.get_session_summary()
print(summary)

# 刷新会话上下文
agent.refresh_session_context()
```

### 处理执行结果

```python
from src.agents import UAVControlAgent

agent = UAVControlAgent()
result = agent.execute("将 drone-001 起飞到 15 米")

# 检查是否成功
if result['success']:
    print("输出:", result['output'])

    # 查看中间步骤
    for step in result['intermediate_steps']:
        print("步骤:", step)
else:
    print("错误:", result['output'])
```

### 批量命令执行

```python
from src.agents import UAVControlAgent

agent = UAVControlAgent()

commands = [
    "列出所有无人机",
    "将第一架无人机起飞到 20 米",
    "移动到坐标 (100, 50, 20)",
    "拍照",
    "返回起始点"
]

for cmd in commands:
    print(f"\n执行: {cmd}")
    result = agent.execute(cmd)
    print(f"结果: {result['output']}")
```

### 错误处理

```python
from src.agents import UAVControlAgent

agent = UAVControlAgent()

try:
    result = agent.execute("无效的命令")
    if not result['success']:
        print("命令执行失败，尝试其他方法")
except Exception as e:
    print(f"发生异常: {e}")
```

---

## 故障排除

### 常见问题

#### 1. 无法连接到 UAV API

**错误**: `API request failed: Connection refused`

**解决方案**:
- 确保 UAV API 服务器正在运行
- 检查 `base_url` 是否正确
- 验证网络连接

```python
# 测试连接
import requests
try:
    response = requests.get("http://localhost:8000/")
    print("API 服务器正常")
except:
    print("API 服务器未运行")
```

#### 2. LLM 提供商连接失败

**错误**: `Failed to connect to LLM provider`

**解决方案**:

对于 Ollama:
```bash
# 确认 Ollama 正在运行
ollama list

# 重启 Ollama
ollama serve
```

对于 OpenAI:
```bash
# 检查 API 密钥
echo $OPENAI_API_KEY

# 测试连接
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

#### 3. Action Input 解析错误

**错误**: `Error parsing JSON input`

**解决方案**:
- 智能体会自动重试
- 确保 LLM 理解 JSON 格式要求
- 可以降低 temperature 使输出更确定

#### 4. 无人机状态错误

**错误**: `Cannot take off: drone not in idle state`

**解决方案**:
- 先检查无人机状态
- 确保无人机处于可以执行命令的状态
- 可能需要先降落或校准

```python
# 检查状态
result = agent.execute("显示 drone-001 的状态")

# 根据状态采取行动
if "idle" in result['output']:
    agent.execute("将 drone-001 起飞")
```

#### 5. 认证失败

**错误**: `Authentication failed: Invalid API key`

**解决方案**:
```python
# 检查 API 密钥配置
from src.config import get_env_api_key, get_uav_api_key

print("LLM API Key:", get_env_api_key())
print("UAV API Key:", get_uav_api_key())
```

### 调试模式

启用调试输出以查看详细信息：

```python
from src.agents import UAVControlAgent

agent = UAVControlAgent(
    debug=True,  # 启用调试模式
    verbose=True
)

result = agent.execute("列出所有无人机")
```

### 日志记录

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('src')

# 使用
from src.agents import UAVControlAgent
agent = UAVControlAgent()
```

### 性能优化

#### 减少冗余 API 调用

```python
# 不好的方式 - 多次调用
for drone_id in drone_ids:
    agent.execute(f"显示 {drone_id} 的状态")

# 好的方式 - 一次调用
agent.execute(f"显示以下无人机的状态: {', '.join(drone_ids)}")
```

#### 调整最大迭代次数

```python
from src.agents.single import UAVAgentGraph

agent = UAVAgentGraph(
    client=client,
    max_iterations=30  # 默认是 50，可根据任务调整
)
```

#### 使用更快的 LLM

```python
# 使用更小更快的模型
agent = UAVControlAgent(
    llm_provider="openai",
    llm_model="gpt-3.5-turbo"  # 比 gpt-4 更快
)
```

---

## 最佳实践

### 1. 始终先检查状态

```python
# 好的做法
agent.execute("列出所有无人机")
agent.execute("检查天气状况")
agent.execute("查看任务进度")

# 然后再执行操作
agent.execute("将第一架无人机起飞")
```

### 2. 处理错误结果

```python
result = agent.execute(command)

if not result['success']:
    # 记录错误
    print(f"错误: {result['output']}")
    # 尝试恢复
    result = agent.execute(f"重试: {command}")
```

### 3. 使用适当的模式

- **简单任务**: 使用单智能体
- **复杂任务**: 使用多智能体协调
- **生产环境**: 启用详细日志和错误处理

### 4. 保护 API 密钥

```python
# 好的做法 - 使用环境变量
import os
api_key = os.getenv("OPENAI_API_KEY")

# 不好的做法 - 硬编码
api_key = "sk-..."  # 不要这样做！
```

### 5. 测试命令

```python
def test_command(agent, command):
    """测试命令并打印结果"""
    print(f"\n测试命令: {command}")
    result = agent.execute(command)
    print(f"成功: {result['success']}")
    print(f"输出: {result['output']}")
    return result

# 使用
agent = UAVControlAgent()
test_command(agent, "列出所有无人机")
```

---

## 示例脚本

### 完整任务脚本

```python
from src.agents import UAVControlAgent
import time

def complete_mission():
    """完成完整的侦察任务"""

    # 初始化
    agent = UAVControlAgent(
        llm_provider="ollama",
        llm_model="llama2",
        verbose=True
    )

    print("=== 开始任务 ===\n")

    # 步骤 1: 获取信息
    agent.execute("列出所有无人机")
    agent.execute("检查天气状况")
    agent.execute("查看任务目标")

    # 步骤 2: 起飞
    agent.execute("将第一架无人机起飞到 20 米")

    # 步骤 3: 执行任务
    agent.execute("访问所有目标位置")

    # 步骤 4: 拍照
    agent.execute("在所有目标位置拍照")

    # 步骤 5: 检查进度
    agent.execute("显示任务进度")

    # 步骤 6: 返回
    agent.execute("返回起始点")

    # 步骤 7: 降落
    agent.execute("降落无人机")

    print("\n=== 任务完成 ===")

if __name__ == "__main__":
    complete_mission()
```

### 多无人机协调脚本

```python
from src.agents.multi import MultiAgentCoordinator

def multi_drone_mission():
    """使用多架无人机完成任务"""

    coordinator = MultiAgentCoordinator(
        llm_provider="openai",
        llm_model="gpt-4o-mini",
        verbose=True
    )

    # 多智能体协调执行
    result = coordinator.execute(
        "使用所有可用无人机完成以下任务："
        "1. Navigator 规划安全路径\n"
        "2. Reconnaissance 在目标位置拍照\n"
        "3. SafetyMonitor 监控电池和安全状况"
    )

    print("执行结果:", result['output'])

if __name__ == "__main__":
    multi_drone_mission()
```
