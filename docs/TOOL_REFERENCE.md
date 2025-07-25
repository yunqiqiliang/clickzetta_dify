# Clickzetta Dify 工具参考手册

## 工具概览

| 工具名称 | 功能 | 输入类型 | 输出类型 |
|---------|------|----------|----------|
| `vector_collection_create` | 创建向量集合 | JSON | 文本 + JSON |
| `vector_collection_list` | 列出向量集合 | JSON | 文本 + JSON |
| `vector_collection_delete` | 删除向量集合 | JSON | 文本 + JSON |
| `vector_collection_optimize` | 优化向量集合 | JSON | 文本 + JSON |
| `vector_insert` | 插入向量数据 | JSON | 文本 + JSON |
| `vector_search` | 搜索相似向量 | JSON | 文本 + JSON |
| `vector_delete` | 删除向量数据 | JSON | 文本 + JSON |
| `lakehouse_sql_query` | 执行SQL查询 | JSON | 文本 + JSON |

## 详细工具说明

### 1. vector_collection_create - 创建向量集合

**功能**: 创建新的向量集合（表），支持自定义维度和元数据字段

**必需参数**:
- `collection_name` (string): 集合名称
- `dimension` (number): 向量维度

**可选参数**:
- `id_type` (string): ID类型，默认"string"，可选"int"
- `metadata_fields` (string): 元数据字段定义，格式："field1:TYPE,field2:TYPE"
- `create_index` (boolean): 是否创建向量索引，默认true
- `schema` (string): 数据库模式名称，默认使用current_schema()的结果

**示例**:
```json
{
  "collection_name": "document_embeddings",
  "dimension": 1536,
  "id_type": "string",
  "metadata_fields": "title:STRING, category:STRING, created_at:TIMESTAMP",
  "create_index": true,
  "schema": "production"
}
```

**输出**:
```json
{
  "success": true,
  "collection_name": "document_embeddings",
  "dimension": 1536,
  "table_created": true,
  "index_created": true
}
```

### 2. vector_collection_list - 列出向量集合

**功能**: 列出指定模式下的所有向量集合及其统计信息

**可选参数**:
- `schema` (string): 数据库模式名称，默认使用current_schema()的结果

**示例**:
```json
{
  "schema": "production"
}
```

**输出**:
```json
{
  "success": true,
  "collections": [
    {
      "name": "document_embeddings",
      "dimension": 1536,
      "vector_count": 1250,
      "has_index": true,
      "description": ""
    }
  ],
  "total_count": 1,
  "schema": "dify"
}
```

### 3. vector_collection_delete - 删除向量集合

**功能**: 删除指定的向量集合及其所有数据

**必需参数**:
- `collection_name` (string): 要删除的集合名称
- `confirm` (boolean): 确认删除，必须为true

**可选参数**:
- `schema` (string): 数据库模式名称，默认使用current_schema()的结果

**示例**:
```json
{
  "collection_name": "old_embeddings",
  "confirm": true,
  "schema": "production"
}
```

**输出**:
```json
{
  "success": true,
  "collection_name": "old_embeddings",
  "deleted": true
}
```

### 4. vector_collection_optimize - 优化向量集合

**功能**: 使用指定的虚拟集群优化向量集合，提升查询和存储性能

**必需参数**:
- `collection_name` (string): 要优化的集合名称
- `optimize_vcluster` (string): 用于执行优化操作的通用类型(GENERAL)虚拟集群名称（其他类型无效）

**可选参数**:
- `schema` (string): 数据库模式名称，默认使用current_schema()的结果

**示例**:
```json
{
  "collection_name": "document_embeddings",
  "optimize_vcluster": "compute_cluster",
  "schema": "production"
}
```

**注意**: 连接参数（用户名、密码、实例等）从插件提供商配置中自动获取，无需在工具参数中指定。

**输出**:
```json
{
  "success": true,
  "collection_name": "document_embeddings",
  "schema": "dify",
  "optimize_vcluster": "compute_cluster",
  "original_vcluster": "default_ap",
  "message": "向量集合优化成功完成"
}
```

**工作流程**:
1. 获取当前虚拟集群（`select current_vcluster()`）
2. 验证优化虚拟集群是否存在且类型正确
3. 切换到指定的优化虚拟集群
4. 执行 `optimize schema.collection_name` 命令
5. 切换回原始虚拟集群
6. 返回优化结果

**集群验证规则**:
- 集群必须存在（通过 `desc vcluster` 命令验证）
- 集群类型必须为 `GENERAL`（其他类型如COMPUTE、STREAM等无效）
- 集群状态必须为 `RUNNING` 或 `SUSPENDED`

**注意事项**:
- **集群类型要求**: 只有通用类型(GENERAL)的虚拟集群能执行优化操作，其他类型会被拒绝
- 优化虚拟集群应具有足够的计算资源
- 优化过程可能需要较长时间，取决于数据量
- 优化后查询性能和存储效率会得到提升
- 系统会自动验证集群可用性，避免使用不合适的集群

### 5. vector_insert - 插入向量数据

**功能**: 向向量集合中插入一个或多个向量

**必需参数**:
- `collection_name` (string): 目标集合名称
- `vectors` (string): 向量数据，JSON数组格式
- `content` (string): 文本内容，JSON数组格式

**可选参数**:
- `ids` (string): 向量ID列表，JSON数组格式
- `metadata` (string): 元数据，JSON数组格式
- `auto_id` (boolean): 是否自动生成ID，默认false
- `schema` (string): 数据库模式名称，默认"dify"

**示例**:
```json
{
  "collection_name": "document_embeddings",
  "vectors": "[[0.1, 0.2, 0.3, ...], [0.4, 0.5, 0.6, ...]]",
  "content": "[\"这是第一个文档的内容\", \"这是第二个文档的内容\"]",
  "metadata": "[{\"title\": \"文档1\", \"category\": \"技术\"}, {\"title\": \"文档2\", \"category\": \"产品\"}]",
  "ids": "[\"doc_001\", \"doc_002\"]",
  "auto_id": false
}
```

**输出**:
```json
{
  "success": true,
  "collection_name": "document_embeddings",
  "inserted_count": 2,
  "inserted_ids": ["doc_001", "doc_002"]
}
```

### 5. vector_search - 搜索相似向量

**功能**: 在向量集合中搜索与查询向量最相似的向量

**必需参数**:
- `collection_name` (string): 目标集合名称
- `query_vectors` (string): 查询向量，JSON数组格式

**可选参数**:
- `top_k` (number): 返回结果数量，默认10
- `metric_type` (string): 距离度量类型，"cosine"或"l2"，默认"cosine"
- `filter_expr` (string): 过滤表达式
- `output_fields` (string): 输出字段列表，逗号分隔
- `schema` (string): 数据库模式名称，默认"dify"

**示例**:
```json
{
  "collection_name": "document_embeddings",
  "query_vectors": "[0.15, 0.25, 0.35, ...]",
  "top_k": 5,
  "metric_type": "cosine",
  "filter_expr": "metadata['category'] = '技术'",
  "output_fields": "title,category"
}
```

**输出**:
```json
{
  "success": true,
  "collection_name": "document_embeddings",
  "query_count": 1,
  "top_k": 5,
  "metric_type": "cosine",
  "total_results": 5,
  "results": [
    {
      "query_index": 0,
      "results": [
        {
          "id": "doc_001",
          "page_content": "这是第一个文档的内容",
          "metadata": {"title": "文档1", "category": "技术"},
          "distance": 0.1234
        }
      ]
    }
  ]
}
```

### 6. vector_delete - 删除向量数据

**功能**: 从向量集合中删除指定的向量

**必需参数**:
- `collection_name` (string): 目标集合名称

**可选参数**:
- `ids` (string): 要删除的向量ID列表，JSON数组格式
- `filter_expr` (string): 删除条件表达式
- `schema` (string): 数据库模式名称，默认"dify"

**注意**: `ids` 和 `filter_expr` 至少提供一个

**示例**:
```json
{
  "collection_name": "document_embeddings",
  "ids": "[\"doc_001\", \"doc_002\"]"
}
```

**输出**:
```json
{
  "success": true,
  "collection_name": "document_embeddings",
  "deleted_count": 2
}
```

### 7. lakehouse_sql_query - 执行SQL查询

**功能**: 在Lakehouse中执行任意SQL查询

**必需参数**:
- `sql` (string): 要执行的SQL语句

**可选参数**:
- `fetch_size` (number): 获取结果的批量大小，默认1000

**示例**:
```json
{
  "sql": "SELECT id, page_content, metadata FROM dify.document_embeddings WHERE metadata['category'] = '技术' LIMIT 10",
  "fetch_size": 1000
}
```

**输出**:
```json
{
  "success": true,
  "sql": "SELECT id, page_content, metadata FROM dify.document_embeddings WHERE metadata['category'] = '技术' LIMIT 10",
  "row_count": 10,
  "columns": ["id", "page_content", "metadata"],
  "data": [
    ["doc_001", "这是第一个文档的内容", {"title": "文档1", "category": "技术"}]
  ]
}
```

## 使用最佳实践

### 1. 向量集合管理
- 使用有意义的集合名称
- 合理设置向量维度
- 为大规模数据创建索引

### 2. 数据插入
- 使用批量插入提高效率
- 确保向量维度一致
- 提供有用的元数据

### 3. 向量搜索
- 根据需求选择合适的距离度量
- 使用过滤条件缩小搜索范围
- 合理设置top_k值

### 4. 性能优化
- 为向量字段创建HNSW索引
- 使用合适的批量大小
- 避免过于复杂的过滤条件

## Schema 验证

所有向量工具在执行操作前都会验证指定的数据库模式是否存在：

1. **验证机制**: 使用 `desc schema schema_name` 命令检查模式存在性
2. **错误处理**: 如果模式不存在，工具会立即返回错误，不会执行后续操作
3. **默认行为**: 如果未指定schema参数，使用 `select current_schema()` 的结果作为默认值

**验证失败示例**:
```json
{
  "success": false,
  "error": "数据库模式不存在：production",
  "collection_name": "document_embeddings"
}
```

## 错误处理

所有工具都会返回标准的错误格式：

```json
{
  "success": false,
  "error": "错误描述",
  "collection_name": "相关集合名称"
}
```

常见错误类型：
- 连接错误：网络或认证问题
- 参数错误：输入参数格式或值错误
- 数据错误：向量维度不匹配或数据格式错误
- 权限错误：没有足够的数据库权限
- 模式错误：指定的数据库模式不存在