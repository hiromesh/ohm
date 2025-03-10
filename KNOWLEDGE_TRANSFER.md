# ohm 与 OHM 知识转移文档

本文档包含关于ohm原始框架及OHM游戏开发框架的关键知识，用于确保项目开发的连续性。

## 1. ohm 核心架构

### 1.1 基本组件

ohm是一个多智能体框架，主要由以下核心组件构成：

- **Roles(角色)**：不同专业领域的智能体，如ProductManager、Architect、Engineer等
- **Actions(动作)**：角色可以执行的操作，如WritePRD、WriteCode等
- **Messages(消息)**：角色之间通信的载体
- **Environment(环境)**：角色交互的场所
- **Memory(记忆)**：存储角色的上下文历史
- **Context(上下文)**：全局共享的信息

### 1.2 关键目录结构

```
/home/hiro/ohm/
├── ohm/
│   ├── actions/              # 动作定义
│   │   ├── action.py         # 基本动作类
│   │   ├── write_prd.py      # 编写产品需求文档
│   │   ├── write_code.py     # 编写代码
│   │   └── ...
│   ├── roles/                # 角色定义
│   │   ├── role.py           # 基本角色类
│   │   ├── product_manager.py # 产品经理
│   │   ├── architect.py      # 架构师
│   │   ├── engineer.py       # 工程师
│   │   └── ...
│   ├── environment/          # 环境定义
│   │   ├── env.py            # 基本环境
│   ├── context/              # 上下文
│   ├── memory/               # 记忆系统
│   ├── tools/                # 工具集成
│   ├── config/               # 配置
│   └── llm/                  # LLM接口
└── examples/                 # 示例代码
    ├── software_team_simulation.py # 软件团队模拟
```

### 1.3 工作流程

1. **初始化**：创建环境和角色
2. **消息传递**：用户输入转化为消息
3. **角色反应**：角色观察消息，执行动作
4. **生成输出**：动作执行结果作为消息发送给其他角色
5. **迭代**：多轮交互直至完成任务

### 1.4 角色反应模式

ohm的`Role`类支持多种反应模式：

```python
class RoleReactMode(Enum):
    REACT = "react"  # 思考-行动循环
    PLAN_AND_ACT = "plan_and_act"  # 先规划后行动
    BY_ORDER = "by_order"  # 按预定顺序执行动作
```

### 1.5 关键方法

```python
# Role类中的关键方法
async def _observe(self) -> bool  # 观察环境中的消息
async def _think(self) -> None    # 思考下一步行动
async def _act(self) -> Message   # 执行动作
async def react(self) -> Message  # 综合观察-思考-行动流程
```

## 2. OHM游戏开发框架

### 2.1 项目目标

OHM(取自印度梵文中的宇宙声音)是一个专门用于游戏开发的自动化框架，旨在：

1. 自动化游戏开发流程
2. 集成游戏引擎(Unity, Unreal, Godot)和建模工具(Blender, Maya)
3. 模拟完整游戏开发团队
4. 生成可执行的游戏代码和资产

### 2.2 当前目录结构

```
/home/hiro/ohm/
├── ohm/                     # 核心包
│   ├── actions/             # 动作模块(当前为空)
│   ├── environment/         # 环境模块
│   ├── prompts/             # 提示模板
│   ├── roles/               # 角色模块(当前为空)
│   ├── templates/           # 项目模板
│   └── tools/               # 工具接口
├── examples/                # 示例
├── tests/                   # 测试
├── requirements.txt         # 依赖
├── setup.py                 # 安装脚本
└── README.md                # 文档
```

### 2.3 建议的扩展结构

```
/home/hiro/ohm/ohm/
├── actions/
│   ├── game_design/         # 游戏设计相关动作
│   ├── development/         # 开发相关动作
│   └── testing/             # 测试相关动作
├── roles/
│   ├── director.py          # 游戏总监
│   ├── designer.py          # 游戏设计师
│   ├── programmer.py        # 游戏程序员
│   ├── artist.py            # 游戏美术师
│   └── tester.py            # 游戏测试员
├── rag/                     # RAG系统
├── learning/                # 经验学习
├── llm/                     # LLM接入
├── config/                  # 配置系统
├── memory/                  # 记忆系统
└── utils/                   # 工具函数
```

### 2.4 核心角色设计

每个角色继承自ohm的`Role`类，但针对游戏开发添加特殊属性和方法：

```python
class GameDirector(Role):
    """游戏总监，负责项目管理和团队协调"""
    def __init__(self, **kwargs):
        super().__init__(name="GameDirector", profile="游戏总监", **kwargs)
        self.set_actions([AnalyzeGameRequirements, AssignGameTasks])

class GameDesigner(Role):
    """游戏设计师，负责游戏机制、关卡和玩法设计"""
    def __init__(self, **kwargs):
        super().__init__(name="GameDesigner", profile="游戏设计师", **kwargs)
        self.set_actions([DesignGameConcept, DesignGameMechanics, DesignGameLevels])
```

### 2.5 核心动作设计

```python
class DesignGameConcept(Action):
    """设计游戏概念和核心理念"""
    def __init__(self):
        super().__init__(name="DesignGameConcept", 
                         description="设计游戏的概念、理念、目标受众和独特卖点")

class WriteGameCode(Action):
    """编写游戏代码"""
    def __init__(self):
        super().__init__(name="WriteGameCode", 
                         description="编写实现游戏功能和机制的代码")
```

### 2.6 游戏开发环境

```python
class GameDevEnv(MGXEnv):
    """游戏开发专用环境，扩展MGXEnv以支持游戏开发流程"""
    
    def __init__(self, context: Context = None):
        super().__init__(context=context)
        self.game_engine = None
        self.modeling_tools = []
        
    def set_game_engine(self, engine_type: str):
        """设置游戏引擎类型 (Unity, Unreal, Godot等)"""
        # 实现游戏引擎选择逻辑
```

### 2.7 游戏开发流程

1. **需求分析**：分析用户输入的游戏创意，提取关键要素
2. **概念设计**：创建游戏概念文档，定义核心玩法和目标受众
3. **机制设计**：详细设计游戏机制、玩家互动和游戏循环
4. **关卡设计**：规划游戏关卡、难度曲线和进程
5. **代码实现**：编写实现游戏功能的代码
6. **资产创建**：创建游戏所需的视觉和音频资产
7. **游戏测试**：进行功能和体验测试，寻找问题
8. **迭代优化**：根据测试反馈进行改进和优化

### 2.8 关键扩展点

1. **RAG系统扩展**：添加游戏设计模式库、引擎文档和代码示例
2. **LLM优化**：针对游戏开发任务的特定提示模板
3. **工具集成**：与Unity、Unreal、Blender等外部工具的API集成
4. **记忆系统增强**：适用于长期游戏项目的上下文管理
5. **经验学习**：从成功游戏案例中提取模式和最佳实践

## 3. 从ohm到OHM的关键适配

### 3.1 保留组件

- **基本消息系统**：保留ohm的消息传递机制
- **角色与动作框架**：保留并扩展为游戏开发角色与动作
- **上下文和记忆系统**：保留核心功能，为游戏开发优化

### 3.2 主要修改

- **特定角色**：替换软件开发角色为游戏开发角色
- **特定动作**：替换软件开发动作为游戏开发动作
- **环境扩展**：扩展环境支持游戏引擎和建模工具
- **工具集成**：添加游戏开发工具的API接口

### 3.3 开发优先级

1. **第一阶段**：实现基本游戏需求分析和设计文档生成
2. **第二阶段**：添加游戏代码生成功能
3. **第三阶段**：集成外部游戏引擎和建模工具API

## 4. 实现考虑事项

### 4.1 游戏引擎集成

关键挑战在于与各引擎API的集成，需要：
- 基本命令执行接口
- 项目创建和管理
- 代码文件生成与导入
- 资产管理

### 4.2 知识库增强

为了提高生成质量，需要扩展RAG系统的游戏开发知识：
- 游戏设计模式库
- 引擎特定的代码示例
- 常见游戏机制实现方法
- 资产创建最佳实践

### 4.3 从ohm复用的关键类

- `Role`类：核心角色抽象
- `Action`类：动作抽象
- `Message`类：消息格式
- `Environment`类：基本环境
- `Memory`类：记忆系统

### 4.4 待解决问题

1. 如何处理游戏资产创建流程的自动化
2. 如何进行游戏平衡性测试
3. 如何集成多平台部署
4. 如何处理不同游戏引擎的特殊要求

## 5. ohm关键源码理解

### 5.1 Role.react 方法

```python
async def react(self) -> Message:
    """Determine how to react to messages based on reaction mode"""
    if self.rc.react_mode == RoleReactMode.REACT or self.rc.react_mode == RoleReactMode.BY_ORDER:
        rsp = await self._react()
    elif self.rc.react_mode == RoleReactMode.PLAN_AND_ACT:
        rsp = await self._plan_and_act()
    else:
        raise ValueError(f"Unsupported react mode: {self.rc.react_mode}")
    return rsp
```

### 5.2 RoleZero._think 方法

这个方法是角色思考过程的核心，需要被游戏开发角色适当扩展，以考虑游戏设计和开发的特殊需求。

### 5.3 Environment.publish_message 方法

消息发布是角色间协作的基础，OHM需要确保消息可以包含游戏相关信息，如资产引用和引擎特定参数。

### 5.4 SoftwareTeamSimulation 类

这个类是OHM游戏开发团队模拟的参考模板，需要适配为游戏开发流程。

## 6. 总结

OHM框架在ohm基础上，为游戏开发任务提供专门优化，保留核心架构同时扩展游戏开发特定功能。通过角色、动作和环境的领域特定适配，以及与游戏引擎和建模工具的集成，OHM将自动化游戏开发流程并生成高质量游戏代码和资产。

---

此文档旨在传递开发连续性所需的关键信息，确保新的开发者可以理解ohm和OHM框架的核心概念和实现细节。
