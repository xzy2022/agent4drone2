# Agent4Drone2 迁移指南

本文档帮助你从旧的代码结构迁移到重构后的模块化架构。

## 目录

- [迁移概述](#迁移概述)
- [自动迁移](#自动迁移)
- [手动迁移](#手动迁移)
- [迁移示例](#迁移示例)
- [兼容性说明](#兼容性说明)
- [常见问题](#常见问题)

---

## 迁移概述

### 旧结构 vs 新结构

#### 旧结构（根目录文件）
```
agent4drone2/
├── uav_agent.py           # 单一文件包含所有智能体逻辑
├── uav_api_client.py      # API 客户端
├── uav_langchain_tools.py # LangChain 工具
└── main.py                # GUI 应用
```

#### 新结构（模块化）
```
agent4drone2/
├── src/
│   ├── agents/              # 智能体实现
│   │   ├── legacy_adapter.py    # 向后兼容适配器
│   │   ├── single/              # 单智能体
│   │   └── multi/               # 多智能体
│   ├── api_client/          # API 客户端
│   ├── tools/               # LangChain 工具
│   ├── config/              # 配置管理
│   ├── prompts/             # 提示词
│   ├── state/               # 状态定义
│   └── utils/               # 工具函数
└── main.py                  # GUI 应用（无需修改）
```

### 迁移优势

- ✅ **无需修改现有代码**: 通过适配器层保持向后兼容
- ✅ **模块化**: 清晰的职责分离
- ✅ **可扩展**: 易于添加新功能
- ✅ **可维护**: 更好的代码组织
- ✅ **可测试**: 独立的模块更容易测试

---

## 自动迁移

### 使用适配器（推荐）

对于大多数用户，无需任何代码修改。适配器会自动将旧 API 调用转发到新架构。

#### 旧代码（继续工作）
```python
from uav_agent import UAVControlAgent

agent = UAVControlAgent(
    base_url="http://localhost:8000",
    llm_provider="ollama",
    llm_model="llama2"
)

result = agent.execute("起飞无人机")
```

#### 新代码（自动使用新架构）
```python
from src.agents import UAVControlAgent

# 相同的接口，内部使用新架构
agent = UAVControlAgent(
    base_url="http://localhost:8000",
    llm_provider="ollama",
    llm_model="llama2"
)

result = agent.execute("起飞无人机")
```

### main.py 迁移

如果你使用 `main.py`（GUI 应用），只需更改导入语句：

#### 修改前
```python
from uav_agent import UAVControlAgent, load_llm_settings, prompt_user_for_llm_config
```

#### 修改后
```python
from src.agents import UAVControlAgent, load_llm_settings, prompt_user_for_llm_config
```

**这就是全部！** GUI 应用的其余部分无需修改。

---

## 手动迁移

### 步骤 1: 更新导入

#### UAVControlAgent

**旧导入**:
```python
from uav_agent import UAVControlAgent
```

**新导入**:
```python
from src.agents import UAVControlAgent
```

#### API 客户端

**旧导入**:
```python
from uav_api_client import UAVAPIClient
```

**新导入**:
```python
from src.api_client import UAVAPIClient
```

#### 工具

**旧导入**:
```python
from uav_langchain_tools import create_uav_tools
```

**新导入**:
```python
from src.tools import create_uav_tools
```

#### 配置

**旧代码**:
```python
from uav_agent import load_llm_settings, get_env_api_key
```

**新代码**:
```python
from src.config import load_llm_settings, get_env_api_key
```

### 步骤 2: 更新直接使用（高级用法）

如果你想直接使用新架构而不是通过适配器：

#### 旧代码
```python
from uav_agent import UAVControlAgent

agent = UAVControlAgent(
    base_url="http://localhost:8000",
    llm_provider="ollama",
    llm_model="llama2"
)
```

#### 新代码（直接使用新架构）
```python
from src.api_client import UAVAPIClient
from src.agents.single import UAVAgentGraph

client = UAVAPIClient(base_url="http://localhost:8000")
agent = UAVAgentGraph(
    client=client,
    llm_provider="ollama",
    llm_model="llama2"
)
```

**注意**: 直接使用新架构时，API 完全兼容，但类名变为 `UAVAgentGraph`。

### 步骤 3: 使用多智能体功能（新功能）

如果你想使用新的多智能体协调功能：

```python
from src.api_client import UAVAPIClient
from src.agents.multi import MultiAgentCoordinator

coordinator = MultiAgentCoordinator(
    client=UAVAPIClient(),
    llm_provider="openai",
    llm_model="gpt-4o-mini"
)

result = coordinator.execute("侦察所有目标")
```

---

## 迁移示例

### 示例 1: 基本脚本

#### 旧代码
```python
from uav_agent import UAVControlAgent

# 初始化
agent = UAVControlAgent(
    base_url="http://localhost:8000",
    llm_provider="ollama",
    llm_model="llama2"
)

# 执行命令
result = agent.execute("起飞无人机")
print(result['output'])

# 交互模式
agent.run_interactive()
```

#### 新代码（选项 1: 使用适配器）
```python
from src.agents import UAVControlAgent

# 完全相同的代码
agent = UAVControlAgent(
    base_url="http://localhost:8000",
    llm_provider="ollama",
    llm_model="llama2"
)

result = agent.execute("起飞无人机")
print(result['output'])

agent.run_interactive()
```

#### 新代码（选项 2: 直接使用新架构）
```python
from src.api_client import UAVAPIClient
from src.agents.single import UAVAgentGraph

client = UAVAPIClient(base_url="http://localhost:8000")
agent = UAVAgentGraph(
    client=client,
    llm_provider="ollama",
    llm_model="llama2"
)

result = agent.execute("起飞无人机")
print(result['output'])

agent.run_interactive()
```

### 示例 2: 自定义配置

#### 旧代码
```python
from uav_agent import UAVControlAgent, load_llm_settings

# 加载配置
settings = load_llm_settings()

# 初始化
agent = UAVControlAgent(
    base_url="http://localhost:8000",
    llm_provider=settings['provider'],
    llm_model=settings['model'],
    llm_api_key=settings.get('api_key')
)
```

#### 新代码（使用适配器）
```python
from src.agents import UAVControlAgent
from src.config import load_llm_settings

# 完全相同的代码
settings = load_llm_settings()

agent = UAVControlAgent(
    base_url="http://localhost:8000",
    llm_provider=settings['provider'],
    llm_model=settings['model'],
    llm_api_key=settings.get('api_key')
)
```

### 示例 3: 直接使用 API 客户端

#### 旧代码
```python
from uav_api_client import UAVAPIClient

client = UAVAPIClient(base_url="http://localhost:8000")
drones = client.list_drones()
```

#### 新代码
```python
from src.api_client import UAVAPIClient

# 完全相同的代码
client = UAVAPIClient(base_url="http://localhost:8000")
drones = client.list_drones()
```

### 示例 4: 使用工具

#### 旧代码
```python
from uav_langchain_tools import create_uav_tools
from uav_api_client import UAVAPIClient

client = UAVAPIClient()
tools = create_uav_tools(client)
```

#### 新代码
```python
from src.tools import create_uav_tools
from src.api_client import UAVAPIClient

# 完全相同的代码
client = UAVAPIClient()
tools = create_uav_tools(client)
```

---

## 兼容性说明

### 完全兼容的功能

以下功能在迁移后**完全兼容**，无需代码修改：

- ✅ `UAVControlAgent` 类的所有方法
- ✅ `execute(command)` 方法
- ✅ `run_interactive()` 方法
- ✅ `refresh_session_context()` 方法
- ✅ `get_session_summary()` 方法
- ✅ `load_llm_settings()` 函数
- ✅ `prompt_user_for_llm_config()` 函数
- ✅ `UAVAPIClient` 类的所有方法
- ✅ 返回值格式（`{'success': bool, 'output': str, 'intermediate_steps': list}`）

### 新增功能

新架构添加的功能（可选使用）：

- 🆕 多智能体协调 (`MultiAgentCoordinator`)
- 🆕 专业化智能体（`NavigatorAgent`, `ReconnaissanceAgent`, `Safe
tyMonitorAgent`）
- 🆕 改进的配置管理 (`LLMProviderConfig`)
- 🆕 工具注册表 (`UAVToolsRegistry`)
- 🆕 状态定义 (`UAVAgentState`, `MultiAgentState`)

### 已移除/更改的功能

**无**。所有旧功能通过适配器保持可用。

---

## 常见问题

### Q1: 我必须立即迁移吗？

**A**: 不必须。旧文件（`uav_agent.py`, `uav_api_client.py` 等）仍然可以工作。但建议逐步迁移到新架构以获得更好的可维护性。

### Q2: 迁移会破坏我的现有代码吗？

**A**: 不会。适配器层确保 100% 向后兼容。只需更改导入语句即可。

### Q3: 我应该使用适配器还是直接使用新架构？

**A**:
- **使用适配器**: 如果你想最小化更改，现有代码继续工作
- **直接使用新架构**: 如果你想利用新功能或更好的代码组织

### Q4: 旧文件会被删除吗？

**A**: 建议保留旧文件作为备份，直到确认迁移成功。可以重命名为 `uav_agent.py.bak` 等。

### Q5: 如何测试迁移是否成功？

**A**: 运行以下测试：

```python
# 测试脚本
from src.agents import UAVControlAgent

agent = UAVControlAgent()

# 测试基本功能
result = agent.execute("列出所有无人机")
assert result['success'], "迁移失败"

print("迁移成功！")
```

### Q6: 多智能体模式是必须的吗？

**A**: 不是。单智能体模式仍然完全支持。多智能体是一个可选的增强功能。

### Q7: 配置文件格式变化了吗？

**A**: `llm_settings.json` 格式保持兼容。新架构还提供了更好的配置类（`LLMProviderConfig`），但这是可选的。

### Q8: 如何回滚到旧代码？

**A**: 只需恢复导入语句：

```python
# 从新代码回滚
from src.agents import UAVControlAgent

# 回到旧代码
from uav_agent import UAVControlAgent
```

---

## 迁移清单

### 阶段 1: 准备（可选）

- [ ] 备份现有代码
- [ ] 阅读 [架构概述](ARCHITECTURE.md)
- [ ] 阅读 [API 参考](API_REFERENCE.md)

### 阶段 2: 基本迁移（推荐）

- [ ] 更新 `main.py` 中的导入语句
- [ ] 测试基本功能是否正常
- [ ] 运行现有测试脚本

### 阶段 3: 验证（推荐）

- [ ] 测试所有现有功能
- [ ] 检查日志输出
- [ ] 验证错误处理

### 阶段 4: 高级迁移（可选）

- [ ] 直接使用新架构（绕过适配器）
- [ ] 尝试多智能体功能
- [ ] 使用新的配置管理
- [ ] 删除旧文件

---

## 迁移脚本

### 自动更新导入

创建一个脚本来自动更新导入：

```python
#!/usr/bin/env python3
"""
迁移助手：自动更新导入语句
"""
import os
import re

def update_imports_in_file(file_path):
    """更新文件中的导入语句"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 导入映射
    import_mappings = {
        r'from uav_agent import': 'from src.agents import',
        r'from uav_api_client import': 'from src.api_client import',
        r'from uav_langchain_tools import': 'from src.tools import',
        r'import uav_agent': 'import src.agents',
        r'import uav_api_client': 'import src.api_client',
        r'import uav_langchain_tools': 'import src.tools',
    }

    # 应用替换
    for old_pattern, new_pattern in import_mappings.items():
        content = re.sub(old_pattern, new_pattern, content)

    # 如果有更改，写回文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已更新: {file_path}")
        return True
    else:
        print(f"⏭️  无需更改: {file_path}")
        return False

def migrate_project(root_dir='.'):
    """迁移整个项目"""
    python_files = []

    # 查找所有 Python 文件
    for root, dirs, files in os.walk(root_dir):
        # 跳过 src 和虚拟环境目录
        if 'src' in root or 'venv' in root or '.git' in root:
            continue

        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    print(f"找到 {len(python_files)} 个 Python 文件\n")

    updated_count = 0
    for file_path in python_files:
        if update_imports_in_file(file_path):
            updated_count += 1

    print(f"\n✨ 迁移完成！更新了 {updated_count} 个文件")

if __name__ == "__main__":
    print("=== Agent4Drone2 迁移助手 ===\n")
    migrate_project()
```

使用方法：

```bash
# 运行迁移脚本
python migrate.py

# 然后测试你的应用
python main.py
```

---

## 总结

### 快速迁移（5 分钟）

1. 更新导入语句：
   ```python
   from src.agents import UAVControlAgent
   ```

2. 测试基本功能：
   ```python
   agent = UAVControlAgent()
   result = agent.execute("列出所有无人机")
   ```

3. 如果工作正常，迁移完成！

### 完整迁移（可选）

1. 阅读 [架构概述](ARCHITECTURE.md)
2. 尝试 [新功能](USAGE_GUIDE.md#高级用法)
3. 直接使用新架构（绕过适配器）
4. 删除旧文件

### 需要帮助？

- 查看 [使用指南](USAGE_GUIDE.md) 了解详细示例
- 查看 [API 参考](API_REFERENCE.md) 了解完整 API
- 查看 [架构概述](ARCHITECTURE.md) 了解系统设计

---

## 迁移后的下一步

迁移完成后，你可以：

1. **探索新功能**
   - 尝试多智能体协调
   - 使用专业化智能体
   - 利用改进的配置管理

2. **改进代码**
   - 采用新的模块化结构
   - 使用新的状态定义
   - 实现自定义工具

3. **贡献**
   - 报告问题
   - 提出改进建议
   - 提交 Pull Request

祝你迁移顺利！🚀
