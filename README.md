# Clickzetta Lakehouse Dify Plugin

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](https://python.org)
[![Dify](https://img.shields.io/badge/Dify-Plugin-orange.svg)](https://dify.ai)

以插件方式为 Dify 平台提供 Clickzetta Lakehouse 向量数据库操作能力的工具集。

## 🚀 功能特性

- **向量集合管理** - 创建、列出、删除向量集合
- **向量数据操作** - 插入、搜索、删除向量数据
- **SQL 查询支持** - 执行任意 SQL 查询
- **高性能搜索** - 支持 HNSW 索引和多种距离度量
- **灵活元数据** - 支持 JSON 格式的元数据存储

## 📦 安装使用

### 环境要求
- Python 3.11+
- Dify 平台
- Clickzetta Lakehouse 访问权限

### 快速开始
1. **安装插件**: 按照 [安装指南](docs/CLICKZETTA_PLUGIN_INSTALLATION_GUIDE.md) 在Dify中安装插件
2. **配置连接**: 在插件设置中配置Clickzetta连接信息
3. **使用工具**: 参考 [工具参考手册](docs/TOOL_REFERENCE.md) 使用各种工具

### 配置环境变量
```bash
export LAKEHOUSE_USERNAME="your_username"
export LAKEHOUSE_PASSWORD="your_password"
export LAKEHOUSE_INSTANCE="your_instance_id"
export LAKEHOUSE_SERVICE="api.clickzetta.com"
export LAKEHOUSE_WORKSPACE="your_workspace"
export LAKEHOUSE_VCLUSTER="your_vcluster"
export LAKEHOUSE_SCHEMA="your_schema"
```

## 🛠️ 开发

### 项目结构
```
clickzetta_dify/
├── docs/          # 文档
├── scripts/       # 开发脚本
├── tests/         # 测试用例
├── tools/         # 工具实现
├── provider/      # 提供商配置
└── _assets/       # 资源文件
```

详细的项目结构说明请参考 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

### 运行测试
```bash
python tests/run_all_tests.py
```

### 兼容性测试
```bash
python tests/compatibility/test_consistency.py
python tests/compatibility/test_sql_compatibility.py
```

## 📋 工具列表

| 工具 | 功能 | 说明 |
|------|------|------|
| `vector_collection_create` | 创建向量集合 | 创建新的向量表 |
| `vector_collection_list` | 列出向量集合 | 查看所有向量集合 |
| `vector_collection_delete` | 删除向量集合 | 删除向量集合及数据 |
| `vector_insert` | 插入向量 | 批量插入向量数据 |
| `vector_search` | 搜索向量 | 相似度搜索 |
| `vector_delete` | 删除向量 | 删除指定向量 |
| `lakehouse_sql_query` | SQL查询 | 执行任意SQL查询 |

## 📖 文档

- [安装指南](docs/CLICKZETTA_PLUGIN_INSTALLATION_GUIDE.md) - 在Dify中安装和配置插件
- [工具参考手册](docs/TOOL_REFERENCE.md) - 详细的工具使用说明
- [详细使用指南](docs/DETAILED_README.md) - 完整的功能和使用示例
- [部署说明](docs/DEPLOYMENT.md) - 部署和维护指南
- [使用指南](docs/GUIDE.md) - 开发者使用指南
- [测试报告](docs/TEST_REPORT.md) - 测试结果和性能数据
- [项目结构](PROJECT_STRUCTURE.md) - 项目目录结构说明

## 🧪 测试状态

- ✅ 基础功能测试
- ✅ 向量操作测试
- ✅ SQL兼容性测试
- ✅ 与Dify主项目一致性测试

## 📄 许可证

Apache License 2.0

## 👥 贡献者

- qiliang / Clickzetta Team

## 📞 支持

如有问题或建议，请提交 [Issue](https://github.com/yunqiqiliang/clickzetta_dify/issues)