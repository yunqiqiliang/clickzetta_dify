# 测试指南

## 快速开始

### 1. 安装依赖

```bash
# 安装插件依赖
pip install -r requirements.txt

# 安装测试依赖
pip install -r tests/requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并填入你的 Lakehouse 连接信息：

```bash
cp .env.example .env
# 编辑 .env 文件，填入实际的连接信息
```

### 3. 运行测试

#### 运行所有测试
```bash
cd tests
python run_all_tests.py
```

#### 运行单个测试
```bash
# 测试连接
python tests/test_connection.py

# 测试向量操作
python tests/test_vector_operations.py

# 测试 SQL 查询
python tests/test_sql_query.py
```

## 测试内容

### 1. 连接测试 (`test_connection.py`)
- 验证 Lakehouse 连接配置
- 执行基本查询测试
- 显示当前模式和版本信息

### 2. 向量操作测试 (`test_vector_operations.py`)
- 创建向量集合（表）
- 插入向量数据和元数据
- 向量相似度搜索（带过滤条件）
- 删除向量（按 ID 和条件）
- 列出所有向量集合

### 3. SQL 查询测试 (`test_sql_query.py`)
- 查看表结构
- 统计查询
- 向量搜索 SQL
- 索引信息查询

## 注意事项

1. **环境隔离**：建议在测试环境中运行，避免影响生产数据
2. **权限要求**：需要创建表、索引和执行查询的权限
3. **清理数据**：测试会创建 `test_embeddings` 表，可以手动删除：
   ```sql
   DROP TABLE IF EXISTS test_embeddings;
   ```

## 故障排除

### 连接失败
- 检查 `.env` 文件中的连接参数是否正确
- 确认网络连接和防火墙设置
- 验证用户权限

### 向量维度错误
- 确保测试中的向量维度与表定义一致
- 默认使用 384 维，可通过 `TEST_VECTOR_DIMENSION` 环境变量修改

### 索引创建失败
- 检查是否有创建索引的权限
- 确认索引名在 schema 内唯一