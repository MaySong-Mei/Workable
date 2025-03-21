# Workable

一个支持AI执行的分层工作单元系统。Workable系统提供了一种灵活的方式来组织和管理AI工作单元，支持工作单元的状态转换、消息传递和关系管理。

## 核心概念

Workable系统基于以下核心概念：

- **Workable**：统一的工作单元类，可根据内部状态表现为简单或复杂工作单元
- **原子模式(γ-workable)**：当`is_atom=True`时，表现为不可再分解的基本操作单元
- **复合模式(α-workable)**：当`is_atom=False`时，表现为可包含子工作单元和本地工作单元的复杂工作单元
- **β-workable**：引用的外部工作单元，作为复合模式Workable的子单元

系统通过工作单元的内部状态转换和组合嵌套，为AI任务执行提供了灵活的框架。

## 功能特性

- **统一工作单元设计**：单一Workable类可通过内部状态切换行为方式
- **状态转换**：支持原子与复合状态间的平滑转换而不丢失身份标识
- **分层工作单元管理**：支持工作单元的嵌套和组合
- **内容管理**：管理工作单元的内容和帧（Frames）
- **消息传递系统**：工作单元之间可以发送、处理和归档消息
- **关系管理**：维护工作单元之间的影响和依赖关系
- **可视化工具**：以树形结构展示工作单元的组织结构

## 安装

```bash
# 克隆仓库
git clone https://github.com/username/Workable.git
cd Workable

# 安装开发环境
pip install -e .
```

## 项目结构

```
workable/
├── core/               # 核心模块
│   ├── content.py      # 内容管理
│   ├── exceptions.py   # 异常定义
│   ├── manager.py      # Workable管理器
│   ├── message.py      # 消息系统
│   ├── models.py       # 基础数据模型
│   ├── relation.py     # 关系管理
│   └── workable.py     # 统一Workable类实现
│
├── utils/              # 工具模块
│   └── logging.py      # 日志工具
│
├── visualizer.py       # 可视化工具
│
├── tests/              # 单元测试
│   ├── test_content.py     # 内容管理测试
│   ├── test_exceptions.py  # 异常测试
│   ├── test_logging.py     # 日志测试
│   ├── test_manager.py     # 管理器测试
│   ├── test_message.py     # 消息系统测试
│   ├── test_models.py      # 数据模型测试
│   ├── test_relation.py    # 关系管理测试
│   ├── test_visualizer.py  # 可视化工具测试
│   └── test_workable.py    # Workable类测试
│
└── __init__.py         # 包初始化文件
```

## 基本用法

### 创建工作单元

```python
from workable.core.manager import WorkableManager
from workable.utils.logging import configure_logging

# 配置日志系统
configure_logging(log_level="INFO")

# 创建工作单元管理器
manager = WorkableManager()

# 创建原子模式工作单元(简单工作单元)
code = manager.create_workable(
    name="Hello World代码",
    logic_description="输出Hello World的程序",
    is_atom=True,  # 创建原子模式工作单元
    content='print("Hello, World!")',
    content_type="code"
)

# 创建复合模式工作单元(复杂工作单元)
project = manager.create_workable(
    name="示例项目",
    logic_description="包含代码和文档的项目",
    is_atom=False  # 创建复合模式工作单元
)

# 添加工作单元作为父工作单元的子单元
project.add_child(code)
```

### 工作单元状态转换

```python
# 将原子模式工作单元转换为复合模式
code.make_complex()

# 检查工作单元模式
if not code.is_atom():
    print("代码现在是复合模式工作单元")

# 如果满足条件，可以将复合模式转回原子模式
if len(code.child_workables) == 0:
    code.make_atom()
```

### 消息传递

```python
from workable.core.models import Message

# 创建消息
message = Message(
    content="请添加注释",
    sender=project.uuid,
    receiver=code.uuid
)

# 发送消息
code.message_manager.append(message)

# 处理消息
inbox_msg = code.message_manager.process_next()
if inbox_msg:
    # 处理完成后归档消息
    code.message_manager.archive_message(inbox_msg.id)
```

### 关系管理

```python
from workable.core.models import Relation

# 创建关系
relation = Relation(
    target_uuid=code.uuid,
    meta={"type": "dependency", "priority": "high"}
)

# 添加关系
project.relation_manager.add(relation)

# 检查关系
if project.relation_manager.has_relation(code.uuid):
    # 更新关系元数据
    project.relation_manager.update_meta(
        code.uuid, 
        {"status": "completed"}
    )
```

### 可视化工作单元

```python
from workable.visualizer import WorkableVisualizer

# 创建可视化器
visualizer = WorkableVisualizer()

# 生成树形结构
tree = visualizer.generate_tree(project)
print(tree)

# 导出为JSON
visualizer.export_tree_to_json(project, "project_tree.json")

# 生成ASCII格式的树
ascii_tree = visualizer.generate_ascii_tree(project)
print(ascii_tree)
```

## 测试

```bash
# 运行所有测试
python -m unittest discover -s workable/tests

# 运行特定测试
python -m workable.tests.test_workable

# 使用pytest（如果已安装）
pytest workable/tests
```

## 示例

查看 `example.py` 和 `example2.py` 获取完整的使用示例。

## 许可证

[MIT](LICENSE) 