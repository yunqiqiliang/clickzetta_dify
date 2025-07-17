# Clickzetta Lakehouse Vector Database Plugin for Dify

这是一个以插件方式为 Dify 平台提供 Clickzetta Lakehouse 向量数据库操作能力的工具集。

## 功能概述

本插件提供了完整的向量数据库功能，包括：

### 向量集合管理
- **创建向量集合** (`vector_collection_create`) - 创建新的向量表，支持自定义维度和元数据字段
- **列出向量集合** (`vector_collection_list`) - 查看所有向量集合及其统计信息
- **删除向量集合** (`vector_collection_delete`) - 删除向量集合及其所有数据

### 向量数据操作
- **插入向量** (`vector_insert`) - 批量插入向量数据，支持自动生成 ID 和自定义元数据
- **搜索向量** (`vector_search`) - 高效的相似度搜索，支持 L2 和余弦距离
- **删除向量** (`vector_delete`) - 按 ID 或条件删除向量

### 通用 SQL 功能
- **SQL 查询** (`lakehouse_sql_query`) - 执行任意 SQL 查询，用于高级数据操作

## 主要优势

1. **统一的数据平台** - 向量数据和结构化数据存储在同一系统中
2. **强大的 SQL 支持** - 可以使用 SQL 进行复杂的数据分析和联合查询
3. **灵活的元数据** - 支持 JSON 格式的元数据和额外的结构化字段
4. **成本效益** - 无需部署和维护独立的向量数据库

## 快速开始

### 1. 环境配置

设置连接凭据的环境变量（所有参数都是必需的）：

```bash
export LAKEHOUSE_USERNAME="your_username"           # Lakehouse 用户名
export LAKEHOUSE_PASSWORD="your_password"           # Lakehouse 密码
export LAKEHOUSE_INSTANCE="your_instance_id"        # Lakehouse 实例 ID
export LAKEHOUSE_SERVICE="api.clickzetta.com"       # API 服务端点（根据你的区域可能不同）
export LAKEHOUSE_WORKSPACE="your_workspace"         # 工作空间名称
export LAKEHOUSE_VCLUSTER="your_vcluster"          # 虚拟集群名称
export LAKEHOUSE_SCHEMA="your_schema"              # 数据库模式名称
```

注意：虽然代码中某些参数有默认值（如 workspace=default），但实际使用时需要根据你的 Lakehouse 实例配置来设置正确的值。

或者，你也可以在每次调用工具时直接提供这些参数。

### 2. 创建向量集合

使用 `vector_collection_create` 工具创建一个新的向量集合：

```json
{
  "collection_name": "document_embeddings",
  "dimension": 384,
  "id_type": "string",
  "metadata_fields": "title:STRING, content:STRING, category:STRING",
  "create_index": true
}
```

### 3. 插入向量数据

使用 `vector_insert` 工具插入向量：

```json
{
  "collection_name": "document_embeddings",
  "vectors": [[0.1, 0.2, 0.3, ...], [0.4, 0.5, 0.6, ...]],
  "ids": ["doc1", "doc2"],
  "metadata": [
    {"title": "文档1", "category": "技术"},
    {"title": "文档2", "category": "产品"}
  ]
}
```

### 4. 搜索相似向量

使用 `vector_search` 工具进行相似度搜索：

```json
{
  "collection_name": "document_embeddings",
  "query_vectors": [[0.15, 0.25, 0.35, ...]],
  "top_k": 5,
  "metric_type": "cosine",
  "filter_expr": "metadata['category'] = '技术'"
}
```

## 典型使用场景

### 1. 知识库管理
- 存储文档的向量嵌入
- 支持按类别、标签等元数据过滤
- 结合 SQL 进行复杂的知识检索

### 2. RAG（检索增强生成）
- 为 LLM 提供相关上下文
- 支持多路召回和重排序
- 可以与其他数据表联合查询

### 3. 推荐系统
- 存储用户和物品的向量表示
- 支持实时的相似度计算
- 可以结合用户行为数据进行个性化推荐

## 高级功能

### 混合查询
结合向量搜索和 SQL 条件：

```sql
-- 使用 SQL 查询工具执行
SELECT id, title, 
       L2_DISTANCE(embedding, CAST([0.1, 0.2, ...] AS VECTOR(384))) as distance
FROM document_embeddings
WHERE metadata['category'] = '技术'
  AND created_at > '2024-01-01'
ORDER BY distance
LIMIT 10
```

### 向量索引管理
Lakehouse 支持 HNSW 算法的向量索引，大幅提升搜索性能：

```sql
-- 创建向量索引（使用余弦距离，更适合文本嵌入）
CREATE VECTOR INDEX idx_doc_emb_001 ON document_embeddings(embedding) 
PROPERTIES (
  "distance.function" = "cosine_distance",
  "scalar.type" = "f32"
)

-- 查看索引信息
SHOW INDEX FROM document_embeddings
```

### 批量操作优化
插件支持批量插入，单次可插入数千个向量，提高数据导入效率。

## 性能优化建议

1. **合理设置向量维度** - 根据实际需求选择合适的维度（如 384、768、1536）
2. **创建向量索引** - 对于大规模数据，确保创建 HNSW 索引
3. **使用批量操作** - 尽量批量插入和查询，减少网络开销
4. **优化元数据查询** - 为常用的过滤字段创建单独的列

## 连接参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| username | Lakehouse 用户名 | 环境变量 |
| password | Lakehouse 密码 | 环境变量 |
| instance | Lakehouse 实例 ID | 环境变量 |
| service | 服务端点 | api.clickzetta.com |
| workspace | 工作空间 | default |
| vcluster | 虚拟集群 | default_ap |
| schema | 数据库模式 | public |

## 故障排除

### 连接问题
- 确保环境变量设置正确
- 检查网络连接和防火墙设置
- 验证实例 ID 和凭据

### 性能问题
- 检查是否创建了向量索引
- 考虑调整查询的 top_k 参数
- 使用过滤条件减少搜索范围

### 数据一致性
- 使用事务确保数据完整性
- 定期备份重要的向量数据
- 监控表的大小和性能指标

## 版本信息

- 插件版本：0.0.1
- 支持的 Lakehouse 版本：1.0.0+
- Python 版本：3.11+
- 作者：qiliang / Clickzetta Team

## 许可证

Apache License 2.0