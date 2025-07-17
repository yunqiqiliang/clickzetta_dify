# Clickzetta Dify 插件安装和使用指南

## 目录
1. [前置条件](#前置条件)
2. [在Dify中安装插件](#在dify中安装插件)
3. [配置连接信息](#配置连接信息)
4. [使用工具](#使用工具)
5. [常见问题](#常见问题)

## 前置条件

### 1. 系统要求
- Dify 平台 (支持插件功能)
- Python 3.11+ 运行环境
- Clickzetta Lakehouse 实例和访问权限

### 2. 必需的连接信息
在开始之前，请确保您有以下Clickzetta Lakehouse连接信息：
- 用户名 (Username)
- 密码 (Password)
- 实例ID (Instance ID)
- 服务端点 (Service endpoint)
- 工作空间名称 (Workspace)
- 虚拟集群名称 (VCluster)
- 数据库模式名称 (Schema)

## 在Dify中安装插件

### 方法1：通过插件包文件安装

1. **下载插件包**
   - 从 [GitHub Releases](https://github.com/yunqiqiliang/clickzetta_dify/releases) 下载最新的 `clickzetta_lakehouse.difypkg` 文件
   - 或者使用项目根目录下的 `clickzetta_lakehouse.difypkg` 文件

2. **在Dify中安装**
   - 登录您的Dify实例
   - 进入「工作空间设置」→「插件」
   - 点击「安装插件」按钮
   - 选择「上传插件包」
   - 选择下载的 `clickzetta_lakehouse.difypkg` 文件
   - 点击「安装」

### 方法2：从源代码安装

1. **克隆仓库**
   ```bash
   git clone https://github.com/yunqiqiliang/clickzetta_dify.git
   cd clickzetta_dify
   ```

2. **打包插件**
   ```bash
   # 安装依赖
   pip install -r requirements.txt
   
   # 生成插件包
   python scripts/sign_plugin.py
   ```

3. **安装到Dify**
   - 按照方法1的步骤，使用生成的插件包文件

## 配置连接信息

### 1. 插件配置
安装完成后，您需要配置Clickzetta Lakehouse的连接信息：

1. **进入插件配置页面**
   - 在Dify的「插件」页面中找到「Clickzetta Lakehouse Tools」
   - 点击「配置」按钮

2. **填写连接信息**
   ```
   用户名: your_username
   密码: your_password
   实例ID: your_instance_id
   服务端点: api.clickzetta.com (或您的区域对应端点)
   工作空间: your_workspace
   虚拟集群: your_vcluster
   数据库模式: your_schema
   ```

3. **测试连接**
   - 点击「测试连接」按钮验证配置是否正确
   - 确认连接成功后，点击「保存」

### 2. 环境变量配置（可选）
如果您的Dify实例支持环境变量，也可以通过环境变量配置：

```bash
export LAKEHOUSE_USERNAME="your_username"
export LAKEHOUSE_PASSWORD="your_password"
export LAKEHOUSE_INSTANCE="your_instance_id"
export LAKEHOUSE_SERVICE="api.clickzetta.com"
export LAKEHOUSE_WORKSPACE="your_workspace"
export LAKEHOUSE_VCLUSTER="your_vcluster"
export LAKEHOUSE_SCHEMA="your_schema"
```

## 使用工具

安装和配置完成后，您可以在Dify的工作流或应用中使用以下工具：

### 1. 向量集合管理

#### 创建向量集合 (vector_collection_create)
```json
{
  "collection_name": "my_documents",
  "dimension": 1536,
  "id_type": "string",
  "metadata_fields": "title:STRING, category:STRING",
  "create_index": true
}
```

#### 列出向量集合 (vector_collection_list)
```json
{
  "schema": "dify"
}
```

#### 删除向量集合 (vector_collection_delete)
```json
{
  "collection_name": "my_documents",
  "confirm": true
}
```

### 2. 向量数据操作

#### 插入向量 (vector_insert)
```json
{
  "collection_name": "my_documents",
  "vectors": "[[0.1, 0.2, 0.3, ...], [0.4, 0.5, 0.6, ...]]",
  "content": "[\"第一个文档内容\", \"第二个文档内容\"]",
  "metadata": "[{\"title\": \"文档1\", \"category\": \"技术\"}, {\"title\": \"文档2\", \"category\": \"产品\"}]",
  "ids": "[\"doc1\", \"doc2\"]",
  "auto_id": false
}
```

#### 搜索向量 (vector_search)
```json
{
  "collection_name": "my_documents",
  "query_vectors": "[0.15, 0.25, 0.35, ...]",
  "top_k": 5,
  "metric_type": "cosine",
  "filter_expr": "metadata['category'] = '技术'",
  "output_fields": "title,category"
}
```

#### 删除向量 (vector_delete)
```json
{
  "collection_name": "my_documents",
  "ids": "[\"doc1\", \"doc2\"]",
  "filter_expr": "metadata['category'] = '过期'"
}
```

### 3. SQL查询

#### 执行SQL查询 (lakehouse_sql_query)
```json
{
  "sql": "SELECT id, page_content, metadata FROM dify.my_documents WHERE metadata['category'] = '技术' LIMIT 10",
  "fetch_size": 1000
}
```

## 在工作流中使用

### 1. 创建工作流
1. 在Dify中创建新的工作流
2. 添加工具节点
3. 在工具列表中选择「Clickzetta Lakehouse Tools」下的相应工具

### 2. 配置工具参数
- 根据上述示例配置工具参数
- 可以使用变量来动态传递参数值

### 3. 连接工作流
- 将工具节点连接到其他节点
- 使用工具的输出作为后续节点的输入

## 在应用中使用

### 1. 聊天应用
- 在聊天应用的工具配置中启用Clickzetta工具
- 用户可以通过自然语言触发向量搜索和数据操作

### 2. Agent应用
- 为Agent配置Clickzetta工具权限
- Agent可以自动使用这些工具进行知识检索和数据处理

## 常见问题

### Q1: 插件安装失败
**A:** 请检查：
- Dify版本是否支持插件功能
- 插件包文件是否完整
- 是否有足够的权限安装插件

### Q2: 连接测试失败
**A:** 请检查：
- 网络连接是否正常
- 连接参数是否正确
- Lakehouse实例是否正常运行
- 用户权限是否足够

### Q3: 工具调用失败
**A:** 请检查：
- 参数格式是否正确
- 目标集合是否存在
- 数据格式是否符合要求

### Q4: 向量搜索结果不准确
**A:** 请检查：
- 向量维度是否匹配
- 距离度量类型是否正确
- 索引是否已创建

### Q5: 性能问题
**A:** 建议：
- 为向量字段创建HNSW索引
- 使用合适的批量大小
- 优化查询条件

## 获取帮助

如果遇到问题，请：
1. 查看Dify的系统日志
2. 检查插件的错误信息
3. 参考项目的[详细文档](DETAILED_README.md)
4. 提交[GitHub Issue](https://github.com/yunqiqiliang/clickzetta_dify/issues)

## 更新插件

要更新插件到新版本：
1. 下载新的插件包
2. 在Dify中卸载旧版本
3. 按照安装步骤安装新版本
4. 重新配置连接信息（如果需要）