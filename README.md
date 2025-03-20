# Workable

一个支持AI执行的分层工作单元系统。Workable系统提供了一种灵活的方式来组织和管理AI工作单元，支持工作单元的转换、消息传递和关系管理。

## 核心概念

Workable系统基于以下核心概念：

- **α-workable (ComplexWorkable)**：复杂工作单元，可以包含子工作单元和本地工作单元
- **β-workable**：引用的外部工作单元，作为ComplexWorkable的子单元
- **γ-workable (SimpleWorkable)**：原子工作单元，不可再分解的基本操作单元

系统通过这三种类型的工作单元，以及它们之间的组合、嵌套和转换，为AI任务执行提供了灵活的框架。

## 功能特性

- **分层工作单元管理**：支持工作单元的嵌套和组合
- **内容管理**：管理工作单元的内容和帧（Frames）
- **消息传递系统**：工作单元之间可以发送、处理和归档消息
- **关系管理**：维护工作单元之间的影响和依赖关系
- **可视化工具**：以树形结构展示工作单元的组织结构
- **转换功能**：支持工作单元的类型转换

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
│   └── workable.py     # Workable基类和实现类
│
├── utils/              # 工具模块
│   ├── logging.py      # 日志工具
│   └── visualizer.py   # 可视化工具
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

# 创建简单工作单元
code = manager.create_simple_workable(
    name="Hello World代码",
    logic_description="输出Hello World的程序",
    content_str='print("Hello, World!")',
    content_type="code"
)

# 创建复杂工作单元
project = manager.create_complex_workable(
    name="示例项目",
    logic_description="包含代码和文档的项目"
)

# 添加简单工作单元作为复杂工作单元的子单元
project.add_child(code)
```

### 工作单元转换

```python
from workable.core.workable import convert_simple_to_complex, convert_complex_to_simple

# 将SimpleWorkable转换为ComplexWorkable
complex_code = convert_simple_to_complex(code)

# 将ComplexWorkable转换回SimpleWorkable（需满足转换条件）
simple_workable = convert_complex_to_simple(complex_code)
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
from workable.utils.visualizer import WorkableVisualizer

# 创建可视化器
visualizer = WorkableVisualizer(manager=manager)

# 生成树形结构
tree = visualizer.generate_tree(project.uuid)
print(tree)

# 导出为JSON
json_repr = visualizer.export_tree_to_json(project.uuid)
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

查看 `src/example.py` 获取完整的使用示例。

## 许可证

[MIT](LICENSE) 