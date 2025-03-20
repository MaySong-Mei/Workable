#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Workable框架复杂系统示例 (Example 2)
模拟企业级Web应用程序开发项目的全生命周期
展示深层次工作单元结构、复杂关系网络和多方向消息传递
"""

import os
import json
import uuid
import random
from datetime import datetime

from workable.core.manager import WorkableManager
from workable.core.models import Message, Relation
from workable.core.workable import convert_simple_to_complex, convert_complex_to_simple
from workable.utils.logging import configure_logging
from workable.utils.visualizer import WorkableVisualizer


def create_code_snippet(name, description, language="python"):
    """生成不同语言的代码片段"""
    code_templates = {
        "python": '''
def {func_name}({params}):
    """
    {description}
    """
    # 实现代码
    {code_body}
    return result
''',
        "javascript": '''
/**
 * {description}
 */
function {func_name}({params}) {{
    // 实现代码
    {code_body}
    return result;
}}
''',
        "java": '''
/**
 * {description}
 */
public {return_type} {func_name}({params}) {{
    // 实现代码
    {code_body}
    return result;
}}
''',
        "sql": '''
-- {description}
CREATE PROCEDURE {func_name} ({params})
BEGIN
    -- 实现代码
    {code_body}
    RETURN result;
END;
''',
        "yaml": '''
# {description}
{func_name}:
  {params}
  implementation:
    {code_body}
''',
        "markdown": '''
# {description}

## 概述
{func_name}

## 参数
{params}

## 实现
{code_body}
'''
    }
    
    func_names = {
        "python": ["process_data", "validate_input", "transform_model", "apply_filter"],
        "javascript": ["updateComponent", "renderView", "fetchData", "handleEvent"],
        "java": ["processRequest", "validateAuthorization", "transformEntity", "executeQuery"],
        "sql": ["GetUserData", "UpdateRecords", "CalculateMetrics", "ArchiveData"],
        "yaml": ["build_config", "test_config", "deploy_config", "env_config"],
        "markdown": ["user_guide", "api_doc", "deployment_guide", "troubleshooting"]
    }
    
    params_templates = {
        "python": "data, options=None",
        "javascript": "data, options = {}",
        "java": "Data data, Options options",
        "sql": "IN data_id INT, IN options VARCHAR(255)",
        "yaml": "version: 1.0, env: production",
        "markdown": "version, environment, audience"
    }
    
    code_bodies = {
        "python": ["result = [x for x in data if x.isvalid()]\n    result = process_pipeline(result)",
                  "validation = Validator(schema)\n    result = validation.check(data)"],
        "javascript": ["const processed = data.map(item => transform(item));\n    result = processed.filter(valid);",
                      "const validation = new Validator(schema);\n    result = validation.check(data);"],
        "java": ["List<Result> result = new ArrayList<>();\n    for(Data item : data) {\n        result.add(processor.process(item));\n    }",
                "ValidationResult result = validator.validate(data, options);\n    if (!result.isValid()) {\n        throw new ValidationException();\n    }"],
        "sql": ["SELECT * FROM Data WHERE condition = TRUE INTO result;",
               "UPDATE Records SET Status = 'PROCESSED' WHERE ID = data_id;"],
        "yaml": ["steps:\n  - build\n  - test\n  - deploy",
                "config:\n  timeout: 30\n  retries: 3"],
        "markdown": ["## 功能说明\n\n这里是功能说明的详细内容...",
                   "## 使用步骤\n\n1. 第一步\n2. 第二步\n3. 第三步"]
    }
    
    return_types = {
        "python": "",
        "javascript": "",
        "java": ["List<Result>", "ValidationResult", "ResponseEntity<Data>", "Optional<Entity>"],
        "sql": "",
        "yaml": "",
        "markdown": ""
    }
    
    template = code_templates.get(language, code_templates["python"])
    func_name = random.choice(func_names.get(language, func_names["python"]))
    params = params_templates.get(language, params_templates["python"])
    code_body = random.choice(code_bodies.get(language, code_bodies["python"]))
    return_type = ""
    if language == "java":
        return_type = random.choice(return_types["java"])
    
    return template.format(
        description=description,
        func_name=func_name,
        params=params,
        code_body=code_body,
        return_type=return_type
    )


def create_frontend_system(manager):
    """创建前端系统及其组件"""
    # 创建前端系统
    frontend = manager.create_complex(
        name="前端系统",
        logic_description="Web应用程序的前端实现"
    )
    
    # 创建UI组件模块
    ui_components = manager.create_complex(
        name="UI组件",
        logic_description="可重用的前端UI组件库"
    )
    frontend.add_child(ui_components)
    
    # 添加具体组件
    components = [
        ("按钮组件", "各种类型和样式的按钮实现", "javascript"),
        ("表单组件", "数据输入和验证的表单控件", "javascript"),
        ("导航组件", "应用程序导航菜单和路由", "javascript"),
        ("数据表格", "用于展示和操作表格数据的组件", "javascript"),
        ("弹窗组件", "模态框和对话框实现", "javascript")
    ]
    
    for name, desc, lang in components:
        component = manager.create_simple(
            name=name,
            logic_description=desc,
            content=create_code_snippet(name, desc, lang),
            content_type="code"
        )
        ui_components.add_child(component)
    
    print(f"UI组件数量: {len(ui_components.child_workables)}")
    print(f"UI组件: {ui_components.child_workables}")
    
    # 创建页面模块
    pages = manager.create_complex(
        name="页面模块",
        logic_description="应用程序的各个页面实现"
    )
    frontend.add_child(pages)
    
    # 添加具体页面
    page_list = [
        ("登录页面", "用户认证和登录流程", "javascript"),
        ("仪表盘", "系统主仪表盘和数据概览", "javascript"),
        ("用户管理", "用户信息管理和权限设置", "javascript"),
        ("报表页面", "数据统计和报表展示", "javascript"),
        ("系统设置", "应用程序配置和个性化设置", "javascript")
    ]
    
    for name, desc, lang in page_list:
        page = manager.create_simple(
            name=name,
            logic_description=desc,
            content=create_code_snippet(name, desc, lang),
            content_type="code"
        )
        pages.add_child(page)
    
    # 创建服务模块
    services = manager.create_complex(
        name="前端服务",
        logic_description="前端与后端交互的服务层"
    )
    frontend.add_child(services)
    
    # 添加具体服务
    service_list = [
        ("API客户端", "与后端API通信的客户端实现", "javascript"),
        ("认证服务", "管理用户会话和认证状态", "javascript"),
        ("状态管理", "应用程序状态和数据流管理", "javascript"),
        ("缓存服务", "客户端数据缓存和持久化", "javascript"),
        ("通知服务", "用户通知和消息推送", "javascript")
    ]
    
    for name, desc, lang in service_list:
        service = manager.create_simple(
            name=name,
            logic_description=desc,
            content=create_code_snippet(name, desc, lang),
            content_type="code"
        )
        services.add_child(service)
    
    # 创建本地工作单元
    styles = manager.create_simple(
        name="样式指南",
        logic_description="前端样式规范和主题配置",
        content="""
# 前端样式指南

## 颜色方案
- 主色：#2563EB
- 辅助色：#3B82F6
- 强调色：#1E40AF
- 文本色：#1F2937
- 背景色：#F9FAFB

## 排版
- 标题：Montserrat, sans-serif
- 正文：Inter, sans-serif
- 代码：Fira Code, monospace

## 组件样式规范
各组件需遵循Material Design规范，保持视觉一致性。
        """,
        content_type="text"
    )
    frontend.add_local(styles)
    
    # 转换简单组件为复杂组件
    buttons_component = next(iter(ui_components.child_workables.values()))  # 获取第一个组件
    complex_buttons = convert_simple_to_complex(buttons_component)
    ui_components.child_workables[buttons_component.uuid] = complex_buttons  # 使用原始UUID更新
    
    # 为复杂按钮组件添加子组件
    button_types = [
        ("主按钮", "具有高视觉重要性的主要操作按钮", "javascript"),
        ("次按钮", "次要操作的按钮样式", "javascript"),
        ("图标按钮", "仅包含图标的轻量级按钮", "javascript"),
        ("加载按钮", "具有加载状态的交互按钮", "javascript")
    ]
    
    for name, desc, lang in button_types:
        btn = manager.create_simple(
            name=name,
            logic_description=desc,
            content=create_code_snippet(name, desc, lang),
            content_type="code"
        )
        complex_buttons.add_child(btn)
    
    return frontend


def create_backend_system(manager):
    """创建后端系统及其组件"""
    # 创建后端系统
    backend = manager.create_complex(
        name="后端系统",
        logic_description="Web应用程序的服务器端和业务逻辑实现"
    )
    
    # 创建API模块
    api = manager.create_complex(
        name="API层",
        logic_description="应用程序接口定义和实现"
    )
    backend.add_child(api)
    
    # 添加API端点
    endpoints = [
        ("用户API", "用户相关操作的接口集合", "python"),
        ("认证API", "用户认证和授权接口", "python"),
        ("数据API", "数据查询和操作接口", "python"),
        ("管理API", "系统管理和配置接口", "python"),
        ("报表API", "数据统计和报表生成接口", "python")
    ]
    
    for name, desc, lang in endpoints:
        endpoint = manager.create_simple(
            name=name,
            logic_description=desc,
            content=create_code_snippet(name, desc, lang),
            content_type="code"
        )
        api.add_child(endpoint)
    
    # 创建服务层
    services = manager.create_complex(
        name="服务层",
        logic_description="业务逻辑和领域服务实现"
    )
    backend.add_child(services)
    
    # 添加具体服务
    service_list = [
        ("用户服务", "用户管理和权限控制服务", "python"),
        ("认证服务", "用户认证和会话管理", "python"),
        ("数据服务", "数据访问和处理服务", "python"),
        ("通知服务", "消息通知和事件处理", "python"),
        ("报表服务", "数据统计和报表生成", "python")
    ]
    
    for name, desc, lang in service_list:
        service = manager.create_simple(
            name=name,
            logic_description=desc,
            content=create_code_snippet(name, desc, lang),
            content_type="code"
        )
        services.add_child(service)
    
    # 创建数据访问层
    data_access = manager.create_complex(
        name="数据访问层",
        logic_description="数据库交互和ORM实现"
    )
    backend.add_child(data_access)
    
    # 添加数据访问组件
    dao_list = [
        ("用户DAO", "用户数据访问对象", "python"),
        ("配置DAO", "系统配置数据访问", "python"),
        ("报表DAO", "报表数据访问和查询", "python"),
        ("事务管理", "数据库事务控制", "python"),
        ("缓存管理", "数据缓存和性能优化", "python")
    ]
    
    for name, desc, lang in dao_list:
        dao = manager.create_simple(
            name=name,
            logic_description=desc,
            content=create_code_snippet(name, desc, lang),
            content_type="code"
        )
        data_access.add_child(dao)
    
    # 创建本地工作单元
    config = manager.create_simple(
        name="后端配置",
        logic_description="后端系统配置和环境设置",
        content="""
# 后端系统配置

## 数据库连接
DB_HOST=localhost
DB_PORT=5432
DB_NAME=app_database
DB_USER=app_user
DB_PASSWORD=secure_password

## API设置
API_VERSION=v1
API_PREFIX=/api/v1
RATE_LIMIT=100/minute
TIMEOUT=30

## 安全设置
JWT_SECRET=your-secret-key-here
TOKEN_EXPIRE=3600
ENCRYPTION_KEY=your-encryption-key
        """,
        content_type="text"
    )
    backend.add_local(config)
    
    # 转换用户服务为复杂组件
    user_service = next(iter(services.child_workables.values()))  # 获取第一个组件
    complex_user_service = convert_simple_to_complex(user_service)
    services.child_workables[user_service.uuid] = complex_user_service  # 使用原始UUID更新
    
    # 为用户服务添加子组件
    user_service_components = [
        ("用户创建", "新用户注册和初始化逻辑", "python"),
        ("用户验证", "用户信息验证和安全检查", "python"),
        ("权限控制", "基于角色的访问控制实现", "python"),
        ("用户配置", "用户个性化设置管理", "python")
    ]
    
    for name, desc, lang in user_service_components:
        component = manager.create_simple(
            name=name,
            logic_description=desc,
            content=create_code_snippet(name, desc, lang),
            content_type="code"
        )
        complex_user_service.add_child(component)
    
    return backend


def create_database_system(manager):
    """创建数据库系统及其组件"""
    # 创建数据库系统
    database = manager.create_complex(
        name="数据库系统",
        logic_description="应用程序的数据存储和管理系统"
    )
    
    # 创建表结构模块
    schema = manager.create_complex(
        name="数据库结构",
        logic_description="数据库表结构和关系定义"
    )
    database.add_child(schema)
    
    # 添加数据库表定义
    tables = [
        ("用户表", "存储用户账户和个人信息", "sql"),
        ("角色表", "用户角色和权限定义", "sql"),
        ("配置表", "系统配置和参数存储", "sql"),
        ("日志表", "系统操作和审计日志", "sql"),
        ("数据表", "业务数据存储", "sql")
    ]
    
    for name, desc, lang in tables:
        table = manager.create_simple(
            name=name,
            logic_description=desc,
            content=create_code_snippet(name, desc, lang),
            content_type="code"
        )
        schema.add_child(table)
    
    # 创建存储过程模块
    procedures = manager.create_complex(
        name="存储过程",
        logic_description="数据库存储过程和函数"
    )
    database.add_child(procedures)
    
    # 添加存储过程
    proc_list = [
        ("用户管理过程", "用户数据管理存储过程", "sql"),
        ("数据聚合过程", "数据统计和聚合计算", "sql"),
        ("审计过程", "系统审计和日志记录", "sql"),
        ("数据清理过程", "数据归档和清理操作", "sql"),
        ("报表生成过程", "复杂报表数据生成", "sql")
    ]
    
    for name, desc, lang in proc_list:
        proc = manager.create_simple(
            name=name,
            logic_description=desc,
            content=create_code_snippet(name, desc, lang),
            content_type="code"
        )
        procedures.add_child(proc)
    
    # 创建索引和优化模块
    optimization = manager.create_complex(
        name="索引和优化",
        logic_description="数据库索引和性能优化配置"
    )
    database.add_child(optimization)
    
    # 添加索引和优化项
    optimization_list = [
        ("主键索引", "表主键索引定义", "sql"),
        ("外键索引", "表关系和外键索引", "sql"),
        ("查询索引", "常用查询性能优化索引", "sql"),
        ("全文索引", "文本搜索全文索引", "sql"),
        ("性能优化配置", "数据库性能参数设置", "sql")
    ]
    
    for name, desc, lang in optimization_list:
        opt = manager.create_simple(
            name=name,
            logic_description=desc,
            content=create_code_snippet(name, desc, lang),
            content_type="code"
        )
        optimization.add_child(opt)
    
    # 创建本地工作单元
    db_config = manager.create_simple(
        name="数据库配置",
        logic_description="数据库连接和配置信息",
        content="""
# 数据库配置

## 主数据库
ENGINE=PostgreSQL
VERSION=13
HOST=db.example.com
PORT=5432
NAME=production_db
USER=db_admin
PASSWORD=secure_password_here

## 读取副本
READ_REPLICAS=3
REPLICA_PREFIX=replica-
REPLICA_SUFFIX=.example.com

## 连接池
MAX_CONNECTIONS=100
IDLE_TIMEOUT=300
CONNECTION_TIMEOUT=5
        """,
        content_type="text"
    )
    database.add_local(db_config)
    
    return database


def create_devops_system(manager):
    """创建DevOps系统及其组件"""
    # 创建DevOps系统
    devops = manager.create_complex(
        name="DevOps系统",
        logic_description="应用程序的开发、测试、部署和运维流程"
    )
    
    # 创建CI/CD模块
    cicd = manager.create_complex(
        name="CI/CD管道",
        logic_description="持续集成和持续部署流程"
    )
    devops.add_child(cicd)
    
    # 添加CI/CD组件
    cicd_components = [
        ("构建配置", "应用程序构建和打包配置", "yaml"),
        ("测试流程", "自动化测试配置和脚本", "yaml"),
        ("部署配置", "应用程序部署和发布配置", "yaml"),
        ("环境管理", "不同环境的配置和管理", "yaml"),
        ("通知设置", "CI/CD流程状态通知配置", "yaml")
    ]
    
    for name, desc, lang in cicd_components:
        component = manager.create_simple(
            name=name,
            logic_description=desc,
            content=create_code_snippet(name, desc, lang),
            content_type="code"
        )
        cicd.add_child(component)
    
    # 创建基础设施模块
    infrastructure = manager.create_complex(
        name="基础设施",
        logic_description="应用程序运行环境和基础设施配置"
    )
    devops.add_child(infrastructure)
    
    # 添加基础设施组件
    infra_components = [
        ("服务器配置", "应用程序服务器配置", "yaml"),
        ("容器配置", "Docker容器和编排配置", "yaml"),
        ("网络设置", "网络和负载均衡配置", "yaml"),
        ("存储配置", "持久化存储和备份配置", "yaml"),
        ("安全配置", "服务器和应用安全设置", "yaml")
    ]
    
    for name, desc, lang in infra_components:
        component = manager.create_simple(
            name=name,
            logic_description=desc,
            content=create_code_snippet(name, desc, lang),
            content_type="code"
        )
        infrastructure.add_child(component)
    
    # 创建监控模块
    monitoring = manager.create_complex(
        name="监控和告警",
        logic_description="系统监控、日志收集和告警配置"
    )
    devops.add_child(monitoring)
    
    # 添加监控组件
    monitor_components = [
        ("性能监控", "应用程序性能指标监控", "yaml"),
        ("日志管理", "日志收集和分析配置", "yaml"),
        ("告警规则", "监控告警触发条件", "yaml"),
        ("仪表盘", "监控数据可视化配置", "yaml"),
        ("报告生成", "系统状态报告生成配置", "yaml")
    ]
    
    for name, desc, lang in monitor_components:
        component = manager.create_simple(
            name=name,
            logic_description=desc,
            content=create_code_snippet(name, desc, lang),
            content_type="code"
        )
        monitoring.add_child(component)
    
    # 创建本地工作单元
    deployment_guide = manager.create_simple(
        name="部署指南",
        logic_description="系统部署和运维操作指南",
        content="""
# 系统部署指南

## 前置条件
- Docker 20.10+
- Kubernetes 1.22+
- Helm 3.8+
- PostgreSQL 13+

## 部署步骤
1. 配置环境变量
2. 初始化数据库
3. 部署后端服务
4. 部署前端应用
5. 配置网络和负载均衡
6. 设置监控和告警
7. 验证部署状态

## 常见问题排查
详见故障排除章节
        """,
        content_type="text"
    )
    devops.add_local(deployment_guide)
    
    return devops


def create_documentation_system(manager):
    """创建文档系统及其组件"""
    # 创建文档系统
    documentation = manager.create_complex(
        name="文档系统",
        logic_description="项目文档和知识库"
    )
    
    # 创建用户文档模块
    user_docs = manager.create_complex(
        name="用户文档",
        logic_description="面向终端用户的使用指南"
    )
    documentation.add_child(user_docs)
    
    # 添加用户文档组件
    user_doc_components = [
        ("入门指南", "系统基本使用入门", "markdown"),
        ("功能指南", "系统各项功能详细说明", "markdown"),
        ("常见问题", "用户常见问题和解答", "markdown"),
        ("故障排除", "常见问题排查和解决", "markdown"),
        ("视频教程", "系统使用视频教程说明", "markdown")
    ]
    
    for name, desc, lang in user_doc_components:
        component = manager.create_simple(
            name=name,
            logic_description=desc,
            content=f"# {name}\n\n{desc}\n\n## 内容概述\n\n这里是{name}的详细内容...",
            content_type="text"
        )
        user_docs.add_child(component)
    
    # 创建开发文档模块
    dev_docs = manager.create_complex(
        name="开发文档",
        logic_description="面向开发人员的技术文档"
    )
    documentation.add_child(dev_docs)
    
    # 添加开发文档组件
    dev_doc_components = [
        ("架构设计", "系统整体架构和设计原则", "markdown"),
        ("API文档", "API接口定义和使用说明", "markdown"),
        ("数据模型", "数据库设计和模型说明", "markdown"),
        ("开发指南", "开发环境搭建和贡献指南", "markdown"),
        ("测试指南", "测试策略和测试用例编写", "markdown")
    ]
    
    for name, desc, lang in dev_doc_components:
        component = manager.create_simple(
            name=name,
            logic_description=desc,
            content=f"# {name}\n\n{desc}\n\n## 内容概述\n\n这里是{name}的详细内容...",
            content_type="text"
        )
        dev_docs.add_child(component)
    
    # 创建运维文档模块
    ops_docs = manager.create_complex(
        name="运维文档",
        logic_description="系统运维和管理文档"
    )
    documentation.add_child(ops_docs)
    
    # 添加运维文档组件
    ops_doc_components = [
        ("部署指南", "系统部署和配置说明", "markdown"),
        ("监控指南", "系统监控和告警配置", "markdown"),
        ("备份恢复", "数据备份和恢复流程", "markdown"),
        ("扩容指南", "系统扩展和性能优化", "markdown"),
        ("安全手册", "系统安全维护和应急响应", "markdown")
    ]
    
    for name, desc, lang in ops_doc_components:
        component = manager.create_simple(
            name=name,
            logic_description=desc,
            content=f"# {name}\n\n{desc}\n\n## 内容概述\n\n这里是{name}的详细内容...",
            content_type="text"
        )
        ops_docs.add_child(component)
    
    # 创建本地工作单元
    doc_standards = manager.create_simple(
        name="文档标准",
        logic_description="项目文档编写规范和标准",
        content="""
# 文档编写标准

## 格式规范
- 使用Markdown格式
- 使用一级标题作为文档标题
- 使用二级标题作为主要章节
- 使用三级标题作为子章节
- 代码块使用```标记并注明语言

## 内容规范
- 每个文档必须包含目的和范围
- 技术文档必须包含示例
- 用户文档必须包含截图
- 避免使用专业术语而不解释
- 保持文档的简洁性和可读性
        """,
        content_type="text"
    )
    documentation.add_local(doc_standards)
    
    return documentation


def main():
    try:
        # 配置日志系统
        configure_logging(log_level="INFO", console=True)
        
        print("=" * 80)
        print("Workable框架复杂系统示例 (Example 2)")
        print("模拟企业级Web应用程序开发项目")
        print("=" * 80)
        
        # 1. 创建工作单元管理器
        print("\n1. 创建工作单元管理器")
        manager = WorkableManager()
        
        # 2. 创建主项目
        print("\n2. 创建企业级Web应用程序项目")
        web_app = manager.create_complex(
            name="企业级Web应用程序",
            logic_description="多层次企业应用平台，包含前后端、数据库、DevOps和文档系统"
        )
        print(f"创建了项目: {web_app.name} (UUID: {web_app.uuid})")
        
        # 3. 创建各个子系统
        print("\n3. 创建各个子系统")
        
        # 3.1 创建前端系统
        print("\n3.1 创建前端系统")
        frontend = create_frontend_system(manager)
        print("前端系统创建完成")
        web_app.add_child(frontend)
        print(f"创建了前端系统 (UUID: {frontend.uuid})")
        
        # 3.2 创建后端系统
        print("\n3.2 创建后端系统")
        backend = create_backend_system(manager)
        print("后端系统创建完成")
        web_app.add_child(backend)
        print(f"创建了后端系统 (UUID: {backend.uuid})")
        
        # 3.3 创建数据库系统
        print("\n3.3 创建数据库系统")
        database = create_database_system(manager)
        print("数据库系统创建完成")
        web_app.add_child(database)
        print(f"创建了数据库系统 (UUID: {database.uuid})")

        # 4. 生成项目树可视化
        print("\n4. 生成项目树可视化")
        visualizer = WorkableVisualizer()
        
        # 生成JSON格式的项目树
        visualizer.export_tree_to_json(web_app, "project_tree.json")
        print("已生成 project_tree.json")
        
        # 生成文本格式的项目树
        text_tree = visualizer.generate_ascii_tree(web_app)
        with open("project_tree.txt", "w", encoding="utf-8") as f:
            f.write(text_tree)
        print("已生成 project_tree.txt")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()