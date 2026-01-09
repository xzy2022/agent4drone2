# Agent4Drone2 API 参考

本文档提供 Agent4Drone2 重构后的完整 API 参考。

## 目录

- [API 客户端 (api_client)](#api-客户端-api_client)
- [UAV 工具 (tools)](#uav-工具-tools)
- [单智能体 (agents/single)](#单智能体-agents/single)
- [多智能体 (agents/multi)](#多智能体-agents/multi)
- [适配器 (agents/legacy_adapter)](#适配器-agents/legacy_adapter)
- [配置管理 (config)](#配置管理-config)
- [状态定义 (state)](#状态定义-state)
- [提示词 (prompts)](#提示词-prompts)

---

## API 客户端 (api_client)

### UAVAPIClient

UAV 控制系统的 API 客户端，封装所有与后端 API 的交互。

#### 初始化

```python
from src.api_client import UAVAPIClient

client = UAVAPIClient(
    base_url: str = "http://localhost:8000",
    api_key: Optional[str] = None
)
```

**参数**:
- `base_url`: UAV API 服务器的基础 URL
- `api_key`: 可选的 API 密钥
  - `None` 或空字符串: USER 角色（基本访问权限）
  - 有效的密钥: SYSTEM 或 ADMIN 角色（基于密钥）

#### 无人机操作方法

##### list_drones()
获取当前会话中的所有无人机。

```python
drones = client.list_drones()
# 返回: List[Dict[str, Any]]
```

##### get_drone_status(drone_id: str)
获取特定无人机的详细状态。

```python
status = client.get_drone_status("drone-001")
# 返回: Dict[str, Any]
```

##### take_off(drone_id: str, altitude: float = 10.0)
命令无人机起飞到指定高度。

```python
result = client.take_off("drone-001", altitude=15.0)
# 返回: Dict[str, Any]
```

##### land(drone_id: str)
命令无人机在当前位置降落。

```python
result = client.land("drone-001")
# 返回: Dict[str, Any]
```

##### move_to(drone_id: str, x: float, y: float, z: float)
移动无人机到指定坐标。

```python
result = client.move_to("drone-001", x=100.0, y=50.0, z=20.0)
# 返回: Dict[str, Any]
```

##### move_along_path(drone_id: str, waypoints: List[Dict[str, float]])
让无人机沿路径点移动。

```python
waypoints = [
    {"x": 50.0, "y": 50.0, "z": 15.0},
    {"x": 100.0, "y": 100.0, "z": 15.0}
]
result = client.move_along_path("drone-001", waypoints)
# 返回: Dict[str, Any]
```

##### change_altitude(drone_id: str, altitude: float)
在保持 X/Y 位置的同时改变无人机高度。

```python
result = client.change_altitude("drone-001", altitude=25.0)
# 返回: Dict[str, Any]
```

##### hover(drone_id: str, duration: Optional[float] = None)
命令无人机在当前位置悬停。

```python
# 无限期悬停
result = client.hover("drone-001")

# 悬停 5 秒
result = client.hover("drone-001", duration=5.0)
# 返回: Dict[str, Any]
```

##### rotate(drone_id: str, heading: float)
旋转无人机面向特定方向（0-360 度）。

```python
# 旋转面向东方（90度）
result = client.rotate("drone-001", heading=90.0)
# 返回: Dict[str, Any]
```

##### move_towards(drone_id: str, distance: float, heading: Optional[float] = None, dz: Optional[float] = None)
沿方向移动无人机指定距离。

```python
# 向当前航向移动 10 米
result = client.move_towards("drone-001", distance=10.0)

# 向东方移动 10 米，同时上升 5 米
result = client.move_towards("drone-001", distance=10.0, heading=90.0, dz=5.0)
# 返回: Dict[str, Any]
```

##### return_home(drone_id: str)
命令无人机返回起始位置。

```python
result = client.return_home("drone-001")
# 返回: Dict[str, Any]
```

##### set_home(drone_id: str)
将当前位置设置为新的起始位置。

```python
result = client.set_home("drone-001")
# 返回: Dict[str, Any]
```

##### calibrate(drone_id: str)
校准无人机传感器。

```python
result = client.calibrate("drone-001")
# 返回: Dict[str, Any]
```

##### charge(drone_id: str, charge_amount: float)
为无人机电池充电（着陆时）。

```python
result = client.charge("drone-001", charge_amount=25.0)
# 返回: Dict[str, Any]
```

##### take_photo(drone_id: str)
使用无人机相机拍照。

```python
result = client.take_photo("drone-001")
# 返回: Dict[str, Any]
```

##### send_message(drone_id: str, target_drone_id: str, message: str)
向另一架无人机发送消息。

```python
result = client.send_message("drone-001", "drone-002", "Hello")
# 返回: Dict[str, Any]
```

##### broadcast(drone_id: str, message: str)
向所有其他无人机广播消息。

```python
result = client.broadcast("drone-001", "Alert")
# 返回: Dict[str, Any]
```

#### 会话操作方法

##### get_current_session()
获取当前任务会话信息。

```python
session = client.get_current_session()
# 返回: Dict[str, Any]
```

##### get_session_data(session_id: str = 'current')
获取会话中的所有实体（无人机、目标、障碍物、环境）。

```python
data = client.get_session_data()
# 返回: Dict[str, Any]
```

##### get_task_progress(session_id: str = 'current')
获取任务完成进度。

```python
progress = client.get_task_progress()
# 返回: Dict[str, Any]
```

#### 环境操作方法

##### get_weather()
获取当前天气条件。

```python
weather = client.get_weather()
# 返回: Dict[str, Any]
```

##### get_targets()
获取会话中的所有目标。

```python
targets = client.get_targets()
# 返回: List[Dict[str, Any]]
```

##### get_waypoints()
获取所有充电站路径点。

```python
waypoints = client.get_waypoints()
# 返回: List[Dict[str, Any]]
```

##### get_obstacles()
获取会话中的所有障碍物。

```python
obstacles = client.get_obstacles()
# 返回: List[Dict[str, Any]]
```

##### get_nearby_entities(drone_id: str)
获取无人机附近的实体（感知半径内）。

```python
nearby = client.get_nearby_entities("drone-001")
# 返回: Dict[str, Any]
```

#### 安全操作方法

##### check_point_collision(x: float, y: float, z: float, safety_margin: float = 0.0)
检查点是否与任何障碍物碰撞。

```python
collision = client.check_point_collision(100.0, 50.0, 20.0, safety_margin=1.0)
# 返回: Optional[Dict[str, Any]]
```

##### check_path_collision(start_x, start_y, start_z, end_x, end_y, end_z, safety_margin=1.0)
检查路径是否与任何障碍物相交。

```python
collision = client.check_path_collision(
    0.0, 0.0, 10.0,  # 起点
    100.0, 100.0, 10.0,  # 终点
    safety_margin=1.0
)
# 返回: Optional[Dict[str, Any]]
```

---

## UAV 工具 (tools)

### UAVToolsRegistry

管理所有 UAV 控制的 LangChain 工具。

#### 初始化

```python
from src.tools import UAVToolsRegistry
from src.api_client import UAVAPIClient

client = UAVAPIClient()
registry = UAVToolsRegistry(client)
```

#### 方法

##### get_tool(name: str)
获取特定名称的工具。

```python
tool = registry.get_tool('take_off')
```

##### get_all_tools() -> list
获取所有注册的工具。

```python
tools = registry.get_all_tools()
```

##### get_tool_names() -> list
获取所有工具名称。

```python
names = registry.get_tool_names()
# 返回: ['list_drones', 'get_session_info', ...]
```

### 工具列表

#### 信息获取工具

##### list_drones()
列出所有可用无人机及其状态。

```python
# 输入: {}
# 输出: JSON 字符串
```

##### get_session_info()
获取当前会话信息。

```python
# 输入: {}
# 输出: JSON 字符串
```

##### get_task_progress()
获取任务进度。

```python
# 输入: {}
# 输出: JSON 字符串
```

##### get_weather()
获取天气条件。

```python
# 输入: {}
# 输出: JSON 字符串
```

##### get_drone_status(input_json: str)
获取特定无人机状态。

```python
# 输入: {"drone_id": "drone-001"}
# 输出: JSON 字符串
```

##### get_nearby_entities(input_json: str)
获取无人机附近的实体。

```python
# 输入: {"drone_id": "drone-001"}
# 输出: JSON 字符串
```

#### 飞行控制工具

##### take_off(input_json: str)
命令无人机起飞。

```python
# 输入: {"drone_id": "drone-001", "altitude": 15.0}
# 输出: JSON 字符串
```

##### land(input_json: str)
命令无人机降落。

```python
# 输入: {"drone_id": "drone-001"}
# 输出: JSON 字符串
```

##### move_to(input_json: str)
移动无人机到指定坐标。

```python
# 输入: {"drone_id": "drone-001", "x": 100.0, "y": 50.0, "z": 20.0}
# 输出: JSON 字符串
```

##### move_towards(input_json: str)
沿方向移动无人机。

```python
# 输入: {"drone_id": "drone-001", "distance": 10.0, "heading": 90.0}
# 输出: JSON 字符串
```

##### change_altitude(input_json: str)
改变无人机高度。

```python
# 输入: {"drone_id": "drone-001", "altitude": 20.0}
# 输出: JSON 字符串
```

##### hover(input_json: str)
命令无人机悬停。

```python
# 输入: {"drone_id": "drone-001", "duration": 5.0}
# 输出: JSON 字符串
```

##### rotate(input_json: str)
旋转无人机。

```python
# 输入: {"drone_id": "drone-001", "heading": 90.0}
# 输出: JSON 字符串
```

##### return_home(input_json: str)
返回起始位置。

```python
# 输入: {"drone_id": "drone-001"}
# 输出: JSON 字符串
```

#### 实用工具

##### set_home(input_json: str)
设置起始位置。

```python
# 输入: {"drone_id": "drone-001"}
# 输出: JSON 字符串
```

##### calibrate(input_json: str)
校准传感器。

```python
# 输入: {"drone_id": "drone-001"}
# 输出: JSON 字符串
```

##### take_photo(input_json: str)
拍照。

```python
# 输入: {"drone_id": "drone-001"}
# 输出: JSON 字符串
```

##### charge(input_json: str)
充电。

```python
# 输入: {"drone_id": "drone-001", "charge_amount": 25.0}
# 输出: JSON 字符串
```

#### 通信工具

##### send_message(input_json: str)
发送消息给另一架无人机。

```python
# 输入: {"drone_id": "drone-001", "target_drone_id": "drone-002", "message": "Hello"}
# 输出: JSON 字符串
```

##### broadcast(input_json: str)
广播消息。

```python
# 输入: {"drone_id": "drone-001", "message": "Alert"}
# 输出: JSON 字符串
```

---

## 单智能体 (agents/single)

### UAVAgentGraph

使用 LangGraph 状态管理的单无人机控制智能体。

#### 初始化

```python
from src.agents.single import UAVAgentGraph
from src.api_client import UAVAPIClient

client = UAVAPIClient()
agent = UAVAgentGraph(
    client: UAVAPIClient,
    llm_provider: str = "ollama",
    llm_model: str = "llama2",
    llm_api_key: Optional[str] = None,
    llm_base_url: Optional[str] = None,
    temperature: float = 0.1,
    verbose: bool = True,
    debug: bool = False
)
```

**参数**:
- `client`: UAV API 客户端实例
- `llm_provider`: LLM 提供商 ('ollama', 'openai', 'openai-compatible')
- `llm_model`: 模型名称
- `llm_api_key`: LLM 提供商的 API 密钥
- `llm_base_url`: LLM API 的自定义基础 URL
- `temperature`: LLM 温度（越低越确定）
- `verbose`: 启用详细输出
- `debug`: 启用调试输出

#### 方法

##### execute(command: str) -> Dict[str, Any]
执行自然语言命令。

```python
result = agent.execute("将第一架无人机起飞至15米")
# 返回: {
#     'success': bool,
#     'output': str,
#     'intermediate_steps': list
# }
```

##### run_interactive()
以交互模式运行智能体。

```python
agent.run_interactive()
```

**交互命令**:
- `quit`, `exit`, `q`: 退出
- `status`: 显示会话摘要
- `help`: 显示示例命令

##### refresh_session_context()
刷新会话上下文信息。

```python
agent.refresh_session_context()
```

##### get_session_summary() -> str
获取当前会话摘要。

```python
summary = agent.get_session_summary()
```

---

## 多智能体 (agents/multi)

### MultiAgentCoordinator

协调多个专业化智能体进行复杂无人机任务。

#### 初始化

```python
from src.agents.multi import MultiAgentCoordinator
from src.api_client import UAVAPIClient

coordinator = MultiAgentCoordinator(
    client: UAVAPIClient,
    llm_provider: str = "ollama",
    llm_model: str = "llama2",
    llm_api_key: Optional[str] = None,
    llm_base_url: Optional[str] = None,
    temperature: float = 0.1,
    verbose: bool = True,
    debug: bool = False
)
```

#### 方法

##### execute(command: str) -> Dict[str, Any]
使用多智能体协调执行命令。

```python
result = coordinator.execute("侦察所有目标并拍照")
# 返回: {
#     'success': bool,
#     'output': str,
#     'intermediate_steps': list,
#     'plan': dict
# }
```

##### get_session_summary() -> str
从协调器视角获取会话摘要。

```python
summary = coordinator.get_session_summary()
```

### 专业化智能体

#### NavigatorAgent

导航员智能体，专精于路径规划和移动。

```python
from src.agents.multi import NavigatorAgent

navigator = NavigatorAgent(
    client: UAVAPIClient,
    llm,  # LLM 实例
    verbose: bool = False
)

result = navigator.execute({'command': '将无人机移动到 (100, 50, 20)'})
```

#### ReconnaissanceAgent

侦察专家智能体，专精于目标识别和摄影。

```python
from src.agents.multi import ReconnaissanceAgent

recon = ReconnaissanceAgent(
    client: UAVAPIClient,
    llm,
    verbose: bool = False
)

result = recon.execute({'command': '在所有目标位置拍照'})
```

#### SafetyMonitorAgent

安全监控员智能体，专精于安全检查和电池管理。

```python
from src.agents.multi import SafetyMonitorAgent

safety = SafetyMonitorAgent(
    client: UAVAPIClient,
    llm,
    verbose: bool = False
)

result = safety.execute({'command': '检查所有无人机的电池状态'})
```

---

## 适配器 (agents/legacy_adapter)

### UAVControlAgent

向后兼容的包装器，保持与原始 `uav_agent.py` 相同的接口。

#### 初始化

```python
from src.agents import UAVControlAgent

agent = UAVControlAgent(
    base_url: str = "http://localhost:8000",
    uav_api_key: Optional[str] = None,
    llm_provider: str = "ollama",
    llm_model: str = "llama2",
    llm_api_key: Optional[str] = None,
    llm_base_url: Optional[str] = None,
    temperature: float = 0.1,
    verbose: bool = True,
    debug: bool = False
)
```

#### 方法

接口与 `UAVAgentGraph` 相同：

- `execute(command: str) -> Dict[str, Any]`
- `run_interactive()`
- `refresh_session_context()`
- `get_session_summary() -> str`

#### 向后兼容函数

##### load_llm_settings(settings_path: str = "llm_settings.json")
从 JSON 文件加载 LLM 设置。

```python
from src.agents import load_llm_settings

settings = load_llm_settings()
```

##### prompt_user_for_llm_config() -> Dict[str, Any]
提示用户选择 LLM 提供商和模型。

```python
from src.agents import prompt_user_for_llm_config

config = prompt_user_for_llm_config()
# 返回: {
#     'llm_provider': str,
#     'llm_model': str,
#     'llm_base_url': str,
#     'llm_api_key': Optional[str],
#     'provider_name': str
# }
```

---

## 配置管理 (config)

### LLMProviderConfig

LLM 提供商配置类。

#### 初始化

```python
from src.config import LLMProviderConfig

config = LLMProviderConfig(
    provider_type: str,          # "ollama", "openai", "openai-compatible"
    base_url: str,               # API 基础 URL
    default_model: str,          # 默认模型
    default_models: Optional[List[str]] = None,  # 可用模型列表
    requires_api_key: bool = False,  # 是否需要 API 密钥
    api_key: Optional[str] = None  # API 密钥
)
```

#### 方法

##### to_dict() -> Dict[str, Any]
转换为字典。

```python
data = config.to_dict()
```

##### from_dict(data: Dict[str, Any]) -> LLMProviderConfig
从字典创建。

```python
config = LLMProviderConfig.from_dict(data)
```

### 配置函数

##### get_default_providers() -> Dict[str, LLMProviderConfig]
获取默认 LLM 提供商配置。

```python
from src.config import get_default_providers

providers = get_default_providers()
# 返回: {
#     "Ollama": LLMProviderConfig(...),
#     "OpenAI": LLMProviderConfig(...)
# }
```

##### load_llm_settings(settings_path: str = "llm_settings.json") -> Optional[Dict[str, Any]]
从 JSON 文件加载 LLM 设置。

```python
from src.config import load_llm_settings

settings = load_llm_settings()
```

##### save_llm_settings(settings: Dict[str, Any], settings_path: str = "llm_settings.json")
保存 LLM 设置到 JSON 文件。

```python
from src.config import save_llm_settings

save_llm_settings(settings, "llm_settings.json")
```

##### get_env_api_key() -> Optional[str]
从环境变量获取 API 密钥。

```python
from src.config import get_env_api_key

api_key = get_env_api_key()  # 检查 OPENAI_API_KEY 或 LLM_API_KEY
```

##### get_uav_api_key() -> Optional[str]
从环境变量获取 UAV API 密钥。

```python
from src.config import get_uav_api_key

api_key = get_uav_api_key()  # 检查 UAV_API_KEY
```

---

## 状态定义 (state)

### UAVAgentState

单无人机智能体状态（TypedDict）。

```python
from src.state import UAVAgentState

state: UAVAgentState = {
    "messages": [],                    # 消息历史
    "session_info": {},                # 会话信息
    "task_progress": {},               # 任务进度
    "drones_status": [],               # 无人机状态
    "intermediate_steps": [],          # 中间步骤
    "current_step": 0,                 # 当前步骤
    "max_iterations": 50,              # 最大迭代次数
    "final_answer": None,              # 最终答案
    "error": None                      # 错误信息
}
```

### MultiAgentState

多智能体协调状态（TypedDict）。

```python
from src.state import MultiAgentState

state: MultiAgentState = {
    "messages": [],                    # 消息历史
    "active_agents": [],               # 活跃智能体列表
    "agent_roles": {},                 # 智能体角色映射
    "task_queue": [],                  # 待执行任务队列
    "completed_tasks": [],             # 已完成任务
    "agent_results": {},               # 各智能体结果
    "shared_context": {},              # 共享上下文
    "current_phase": "",               # 当前阶段
    "final_plan": None,                # 最终计划
    "final_answer": None,              # 最终答案
    "error": None                      # 错误信息
}
```

---

## 提示词 (prompts)

### 单智能体提示词

#### UAV_AGENT_SYSTEM_PROMPT

单智能体的系统提示词常量。

```python
from src.prompts import UAV_AGENT_SYSTEM_PROMPT

print(UAV_AGENT_SYSTEM_PROMPT)
```

#### get_uav_agent_prompt(tool_names: list, tool_descriptions: list) -> str

生成包含工具信息的 UAV 智能体提示词。

```python
from src.prompts import get_uav_agent_prompt

prompt = get_uav_agent_prompt(
    tool_names=['take_off', 'land', 'move_to'],
    tool_descriptions=['起飞到指定高度', '降落无人机', '移动到坐标']
)
```

### 多智能体提示词

#### COORDINATOR_SYSTEM_PROMPT

协调器的系统提示词。

```python
from src.prompts import COORDINATOR_SYSTEM_PROMPT
```

#### NAVIGATOR_AGENT_PROMPT

导航员智能体的系统提示词。

```python
from src.prompts import NAVIGATOR_AGENT_PROMPT
```

#### RECONNAISSANCE_AGENT_PROMPT

侦察专家智能体的系统提示词。

```python
from src.prompts import RECONNAISSANCE_AGENT_PROMPT
```

#### SAFETY_MONITOR_PROMPT

安全监控员智能体的系统提示词。

```python
from src.prompts import SAFETY_MONITOR_PROMPT
```

#### get_multi_agent_prompt(role: str) -> str

获取特定角色的系统提示词。

```python
from src.prompts import get_multi_agent_prompt

prompt = get_multi_agent_prompt('navigator')
# 可选角色: 'coordinator', 'navigator', 'reconnaissance', 'safety'
```

### 错误处理模板

#### PARSING_ERROR_TEMPLATE

Action Input 解析错误的错误消息模板。

```python
from src.prompts import PARSING_ERROR_TEMPLATE

error_msg = PARSING_ERROR_TEMPLATE.format(error="Invalid JSON")
```

---

## 便捷函数

### create_uav_tools(client: UAVAPIClient) -> list

为 LangChain 智能体创建所有 UAV 控制工具。

```python
from src.api_client import UAVAPIClient
from src.tools import create_uav_tools

client = UAVAPIClient()
tools = create_uav_tools(client)
```
