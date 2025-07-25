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

### 快速安装

#### 方法一：下载预构建插件包

从本项目获取插件文件：
- **标准版本**: `clickzetta_lakehouse.difypkg` - 遵循Dify官方标准，适用于大多数环境
- **签名版本**: `clickzetta_lakehouse.signed.difypkg` - 适用于启用第三方签名验证的环境

**获取方式**：
- 直接下载：点击项目页面中的插件文件，然后点击 "Download" 按钮
- 克隆项目：`git clone https://github.com/yunqiqiliang/clickzetta_dify.git`

#### 方法二：自行构建插件包

```bash
# 构建标准版本（默认）
./build.sh

# 构建带签名的版本
./build.sh --sign
```

**构建脚本功能**：
- 🔍 自动验证配置文件
- 📦 生成标准插件包
- 🔐 可选生成签名版本
- ✅ 内置签名验证测试

#### 安装步骤

1. **选择插件包**：
   - 如果服务器禁用了签名验证：使用 `clickzetta_lakehouse.difypkg`
   - 如果服务器启用了第三方签名验证：使用 `clickzetta_lakehouse.signed.difypkg`

2. **服务器端配置**（仅签名版本需要）：
   ```yaml
   # docker-compose.override.yaml
   version: '3.8'
   services:
     plugin_daemon:
       environment:
         THIRD_PARTY_SIGNATURE_VERIFICATION_ENABLED: "true"
         THIRD_PARTY_SIGNATURE_VERIFICATION_PUBLIC_KEYS: "/app/storage/public_keys/clickzetta_server_keypair.public.pem"
   ```
   
   上传公钥到：`docker/volumes/plugin_daemon/public_keys/`

3. **上传安装**：
   - 登录 Dify 管理后台
   - 进入 "插件" → "安装插件" 页面
   - 选择 "本地上传" 方式
   - 上传选择的插件包文件
   - 等待安装完成

4. **配置插件**：在插件设置中配置 Clickzetta 连接参数

5. **开始使用**：插件安装成功后即可在工作流中使用所有Clickzetta工具


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
| `vector_collection_optimize` | 优化向量集合 | 使用指定集群优化向量表性能 |
| `vector_insert` | 插入向量 | 批量插入向量数据 |
| `vector_search` | 搜索向量 | 相似度搜索 |
| `vector_delete` | 删除向量 | 删除指定向量 |
| `lakehouse_sql_query` | SQL查询 | 执行任意SQL查询 |

## 📖 文档

- [构建指南](docs/BUILD_GUIDE.md) - 如何构建和签名插件包
- [安装指南](docs/DIFY_CLICKZETTA_PLUGIN_INSTALLATION_GUIDE.md) - 在Dify中安装和配置插件
- [工具参考手册](docs/TOOL_REFERENCE.md) - 详细的工具使用说明
- [优化工具使用示例](docs/OPTIMIZE_USAGE_EXAMPLE.md) - 向量集合优化工具详细说明
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