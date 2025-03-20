#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Workable框架示例
展示创建工作单元、转换、消息传递、关系管理和可视化功能
"""

import os
import time
import json
from workable.core.manager import WorkableManager
from workable.core.models import Message, Relation
from workable.core.workable import convert_simple_to_complex, convert_complex_to_simple
from workable.utils.logging import configure_logging
from workable.utils.visualizer import WorkableVisualizer


def main():
    # 配置日志系统
    configure_logging(log_level="INFO", console=True)
    
    print("=" * 50)
    print("Workable框架示例")
    print("=" * 50)
    
    # 1. 创建工作单元管理器
    print("\n1. 创建工作单元管理器")
    manager = WorkableManager()
    
    # 2. 创建简单工作单元
    print("\n2. 创建简单工作单元")
    python_code = manager.create_simple(
        name="Python代码",
        logic_description="生成斐波那契数列的Python函数",
        content='''
def fibonacci(n):
    """返回斐波那契数列的前n个数"""
    result = []
    a, b = 0, 1
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result

print(fibonacci(10))  # 输出: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
''',
        content_type="code"
    )
    print(f"创建了简单工作单元: {python_code.name} (UUID: {python_code.uuid})")
    
    documentation = manager.create_simple(
        name="文档",
        logic_description="斐波那契数列算法的说明文档",
        content='''
# 斐波那契数列

斐波那契数列是一个以递归方式定义的数列，形式如下：

```
F(0) = 0
F(1) = 1
F(n) = F(n-1) + F(n-2), 当 n > 1
```

数列的前几项是：0, 1, 1, 2, 3, 5, 8, 13, 21, 34, ...

本实现使用迭代方法而非递归，以提高效率。
''',
        content_type="text"
    )
    print(f"创建了简单工作单元: {documentation.name} (UUID: {documentation.uuid})")
    
    # 3. 创建复杂工作单元
    print("\n3. 创建复杂工作单元")
    project = manager.create_complex(
        name="斐波那契项目",
        logic_description="计算斐波那契数列的完整项目，包含代码和文档"
    )
    print(f"创建了复杂工作单元: {project.name} (UUID: {project.uuid})")
    
    # 4. 添加简单工作单元作为复杂工作单元的子单元
    print("\n4. 添加子工作单元")
    project.add_child(python_code)
    project.add_child(documentation)
    print(f"已将{python_code.name}和{documentation.name}添加为{project.name}的子工作单元")
    
    # 5. 创建一个本地工作单元
    print("\n5. 创建本地工作单元")
    readme = manager.create_simple(
        name="README",
        logic_description="项目说明文件",
        content="# 斐波那契项目\n\n这是一个计算斐波那契数列的项目。",
        content_type="text"
    )
    project.add_local(readme)
    print(f"已将{readme.name}添加为{project.name}的本地工作单元")
    
    # 6. 工作单元转换
    print("\n6. 工作单元转换")
    print("将简单工作单元转换为复杂工作单元...")
    complex_code = convert_simple_to_complex(python_code)
    print(f"转换成功: {complex_code.name} (UUID: {complex_code.uuid})")
    print(f"类型: {type(complex_code).__name__}")
    
    # 7. 消息传递
    print("\n7. 消息传递")
    # 创建消息
    message = Message(
        content="请优化斐波那契函数以支持大数列计算",
        sender=project.uuid,
        receiver=python_code.uuid
    )
    # 发送消息
    python_code.message_manager.append(message)
    print(f"从{project.name}发送消息到{python_code.name}")
    
    # 处理消息
    inbox_msg = python_code.message_manager.process_next()
    if inbox_msg:
        print(f"处理消息: {inbox_msg.content}")
        # 模拟代码更新
        python_code.content_str = '''
def fibonacci(n, memo={}):
    """返回斐波那契数列的前n个数，使用备忘录提高效率"""
    if n in memo:
        return memo[n]
    
    result = []
    a, b = 0, 1
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    
    memo[n] = result
    return result

print(fibonacci(100))  # 支持更大数列
'''
        # 归档消息
        python_code.message_manager.archive_message(inbox_msg.id)
        print("消息已处理并归档")
    
    # 8. 关系管理
    print("\n8. 关系管理")
    # 创建关系
    relation = Relation(
        target_uuid=documentation.uuid,
        meta={"type": "dependency", "priority": "high"}
    )
    # 添加关系
    python_code.relation_manager.add(relation)
    print(f"已为{python_code.name}添加与{documentation.name}的依赖关系")
    
    # 检查关系
    if python_code.relation_manager.has_relation(documentation.uuid):
        # 更新关系元数据
        python_code.relation_manager.update_meta(
            documentation.uuid, 
            {"status": "completed"}
        )
        print("关系元数据已更新")
    
    # 9. 可视化工作单元
    print("\n9. 可视化工作单元")
    # 创建可视化器
    visualizer = WorkableVisualizer(manager=manager)
    
    # 获取Workable对象而不是UUID
    project_obj = manager.get_workable(project.uuid)
    
    # 生成树形结构
    tree = visualizer.generate_tree(project_obj)
    print("\n项目树结构:")
    print(json.dumps(tree, ensure_ascii=False, indent=2))
    
    # 导出为JSON
    json_file = "project_tree.json"
    visualizer.export_tree_to_json(project_obj, json_file)
    print(f"\nJSON树结构已导出到文件: {os.path.abspath(json_file)}")
    
    # 生成ASCII树结构并保存到文件
    ascii_file = "project_tree.txt"
    visualizer.export_ascii_tree_to_file(project_obj, ascii_file)
    print(f"ASCII树结构已导出到文件: {os.path.abspath(ascii_file)}")
    
    print("\n" + "=" * 50)
    print("示例完成！")
    print("=" * 50)


if __name__ == "__main__":
    main() 