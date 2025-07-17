# Clickzetta Dify Plugin - 项目结构

## 目录结构

```
clickzetta_dify/
├── docs/                           # 文档目录
│   ├── DEPLOYMENT.md              # 部署指南
│   ├── GUIDE.md                   # 使用指南
│   └── TEST_REPORT.md             # 测试报告
├── scripts/                        # 脚本目录
│   ├── fix_all_human_descriptions.py    # 修复人类描述脚本
│   ├── fix_human_descriptions.py        # 修复人类描述脚本
│   ├── fix_service_param.py             # 修复服务参数脚本
│   ├── generate_signature.py            # 生成签名脚本
│   ├── remove_connection_params.py      # 移除连接参数脚本
│   ├── sign_plugin.py                   # 插件签名脚本
│   └── update_connection_config.py      # 更新连接配置脚本
├── tests/                          # 测试目录
│   ├── compatibility/             # 兼容性测试
│   │   ├── test_consistency.py   # 一致性测试
│   │   └── test_sql_compatibility.py # SQL兼容性测试
│   ├── tools/                     # 工具测试
│   │   ├── test_collection_list_fix.py  # 集合列表修复测试
│   │   ├── test_plugin_final.py         # 插件最终测试
│   │   ├── test_simple.py              # 简单测试
│   │   ├── test_simple_fix.py          # 简单修复测试
│   │   └── test_tools_updated.py       # 工具更新测试
│   ├── README.md                  # 测试说明
│   ├── fix_yaml_files.py          # 修复YAML文件
│   ├── requirements.txt           # 测试依赖
│   ├── run_all_tests.py           # 运行所有测试
│   ├── test_connection.py         # 连接测试
│   ├── test_dify_tools.py         # Dify工具测试
│   ├── test_plugin_simple.py      # 插件简单测试
│   ├── test_sql_query.py          # SQL查询测试
│   ├── test_sri_protocol.py       # SRI协议测试
│   └── test_vector_operations.py  # 向量操作测试
├── tools/                          # 工具目录
│   ├── lakehouse_connection.py    # 数据库连接
│   ├── lakehouse_sql_query.py     # SQL查询工具
│   ├── lakehouse_sql_query.yaml   # SQL查询配置
│   ├── vector_collection_create.py # 向量集合创建
│   ├── vector_collection_create.yaml # 向量集合创建配置
│   ├── vector_collection_delete.py # 向量集合删除
│   ├── vector_collection_delete.yaml # 向量集合删除配置
│   ├── vector_collection_list.py  # 向量集合列表
│   ├── vector_collection_list.yaml # 向量集合列表配置
│   ├── vector_delete.py           # 向量删除
│   ├── vector_delete.yaml         # 向量删除配置
│   ├── vector_insert.py           # 向量插入
│   ├── vector_insert.yaml         # 向量插入配置
│   ├── vector_search.py           # 向量搜索
│   └── vector_search.yaml         # 向量搜索配置
├── provider/                       # 提供商目录
│   ├── clickzetta_dify.code-workspace # VS Code工作区
│   ├── lakehouse.py               # 提供商实现
│   └── lakehouse.yaml             # 提供商配置
├── _assets/                        # 资源目录
│   └── icon.svg                   # 图标文件
├── main.py                         # 主程序入口
├── manifest.yaml                   # 插件清单
├── requirements.txt                # 依赖文件
├── README.md                       # 项目说明
├── PRIVACY.md                      # 隐私声明
├── PROJECT_STRUCTURE.md            # 项目结构（此文件）
└── clickzetta_lakehouse.difypkg    # 插件包
```

## 核心文件说明

### 主要文件
- `main.py` - 插件主程序入口
- `manifest.yaml` - 插件清单文件，定义插件元数据
- `requirements.txt` - Python依赖包列表
- `README.md` - 项目主要说明文档

### 工具实现
- `tools/` - 所有Dify工具的实现和配置
- `provider/` - 插件提供商的实现和配置

### 测试和脚本
- `tests/` - 各种测试文件，按功能分类
- `scripts/` - 开发和维护脚本
- `docs/` - 项目文档

### 资源文件
- `_assets/` - 图标等资源文件
- `clickzetta_lakehouse.difypkg` - 打包后的插件文件

## 开发流程

1. **开发工具** - 在`tools/`目录中实现新的工具
2. **配置提供商** - 在`provider/`目录中配置提供商
3. **编写测试** - 在`tests/`目录中添加测试用例
4. **运行测试** - 使用`tests/run_all_tests.py`运行所有测试
5. **打包发布** - 使用`scripts/`中的脚本打包和签名

## 版本管理

- 主版本信息在`manifest.yaml`中维护
- 测试报告在`docs/TEST_REPORT.md`中记录
- 部署说明在`docs/DEPLOYMENT.md`中提供