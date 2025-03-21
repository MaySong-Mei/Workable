"""
索引式Workable框架演示
展示索引机制如何解耦数据存储和引用
"""

import sys
import logging
import json

from workable.core.workable import Workable
from workable.core.manager import WorkableManager
from workable.utils.visualizer import WorkableVisualizer


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# 创建管理器
manager = WorkableManager()
visualizer = WorkableVisualizer()


def create_frontend_project():
    """创建前端项目示例"""
    # 创建根Workable
    frontend = manager.create_workable(
        name="前端应用",
        logic_description="React前端应用",
        is_atom=False
    )
    
    # 添加组件
    components = manager.create_workable(
        name="组件",
        logic_description="React组件库",
        is_atom=False
    )
    
    # 添加组件到前端
    frontend.add_child(components)
    
    # 添加具体组件
    button = manager.create_workable(
        name="Button",
        logic_description="按钮组件",
        is_atom=True,
        content="function Button(props) {\n  return <button {...props}>{props.children}</button>;\n}",
        content_type="jsx"
    )
    
    input = manager.create_workable(
        name="Input",
        logic_description="输入框组件",
        is_atom=True,
        content="function Input(props) {\n  return <input {...props} />;\n}",
        content_type="jsx"
    )
    
    # 添加组件到组件库
    components.add_child(button)
    components.add_child(input)
    
    # 添加本地工作单元
    readme = Workable(
        name="README",
        logic_description="组件库说明",
        is_atom=True,
        content_str="# 组件库\n\n这是一个React组件库",
        content_type="markdown"
    )
    components.add_local(readme)
    
    return frontend


def create_backend_project():
    """创建后端项目示例"""
    # 创建根Workable
    backend = manager.create_workable(
        name="后端服务",
        logic_description="Flask后端服务",
        is_atom=False
    )
    
    # 添加API
    api = manager.create_workable(
        name="API",
        logic_description="API端点",
        is_atom=False
    )
    
    # 添加API到后端
    backend.add_child(api)
    
    # 添加具体API
    users_api = manager.create_workable(
        name="UsersAPI",
        logic_description="用户API",
        is_atom=True,
        content="from flask import Blueprint\n\nusers_bp = Blueprint('users', __name__)\n\n@users_bp.route('/users')\ndef get_users():\n    return {'users': []}\n",
        content_type="python"
    )
    
    # 添加API到API端点
    api.add_child(users_api)
    
    return backend


def demonstrate_conversion():
    """演示转换功能"""
    # 创建简单Workable
    simple = manager.create_workable(
        name="配置文件",
        logic_description="应用配置",
        is_atom=True,
        content="{\n  \"port\": 3000,\n  \"debug\": true\n}",
        content_type="json"
    )
    
    print(f"\n原始简单Workable: {simple}")
    print(f"内容: {simple.content_str}")
    
    # 转换为复杂Workable
    complex = simple.make_complex()
    
    print(f"\n转换后的复杂Workable: {complex}")
    
    # 获取本地Workable（原内容）
    locals = complex.get_locals()
    print(f"本地Workable数量: {len(locals)}")
    print(f"本地Workable内容: {locals[0].content_str}")
    
    # 添加子Workable
    child = manager.create_workable(
        name="子配置",
        logic_description="服务配置",
        is_atom=True,
        content="{\n  \"host\": \"localhost\"\n}",
        content_type="json"
    )
    complex.add_child(child)
    
    # 获取子Workable
    children = complex.get_children()
    print(f"子Workable数量: {len(children)}")
    
    # 删除子Workable
    complex.remove_child(child.uuid)
    
    # 转换回简单Workable
    simple_again = complex.make_simple()
    
    print(f"\n再次转换后的简单Workable: {simple_again}")
    print(f"内容: {simple_again.content_str}")


def export_tree_visualization(root, name):
    """导出树可视化"""
    # 输出树JSON
    tree_json = visualizer.export_tree_to_json(root)
    with open(f"{name}_tree.json", "w", encoding="utf-8") as f:
        json.dump(tree_json, f, indent=2, ensure_ascii=False)
    
    # 输出ASCII树
    tree_text = visualizer.generate_ascii_tree(root)
    with open(f"{name}_tree.txt", "w", encoding="utf-8") as f:
        f.write(tree_text)


def main():
    """主函数"""
    print("=== 基于索引的Workable框架演示 ===\n")
    
    # 创建前端项目
    print("创建前端项目...")
    frontend = create_frontend_project()
    
    # 创建后端项目
    print("创建后端项目...")
    backend = create_backend_project()
    
    # 创建完整项目
    project = manager.create_workable(
        name="全栈项目",
        logic_description="完整的全栈Web应用",
        is_atom=False
    )
    
    # 添加前端和后端到项目
    project.add_child(frontend)
    project.add_child(backend)
    
    # 添加本地文档
    docs = Workable(
        name="项目文档",
        logic_description="项目说明文档",
        is_atom=True,
        content_str="# 全栈Web应用\n\n这是一个全栈Web应用的工作单元分解",
        content_type="markdown"
    )
    project.add_local(docs)
    
    # 导出可视化
    print("导出项目树...")
    export_tree_visualization(project, "project")
    
    # 演示转换功能
    print("\n演示转换功能...")
    demonstrate_conversion()
    
    # 打印管理器统计信息
    print("\n管理器统计信息:")
    stats = manager.to_dict()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main() 