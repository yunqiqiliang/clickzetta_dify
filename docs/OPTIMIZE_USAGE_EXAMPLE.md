# 向量集合优化工具使用示例

## 功能简介

`vector_collection_optimize` 工具用于优化ClickZetta Lakehouse中的向量集合，提升查询性能和存储效率。该工具通过指定一个专用的计算集群来执行优化操作，避免影响正常的业务操作。

## 使用场景

1. **性能优化**: 定期优化大型向量集合以提升查询速度
2. **存储优化**: 整理数据文件，减少存储碎片
3. **索引重建**: 重新构建向量索引以获得最佳性能
4. **资源隔离**: 使用专门的计算集群进行优化，不影响生产负载

## 基本用法

```json
{
  "collection_name": "document_embeddings",
  "optimize_vcluster": "compute_cluster"
}
```

### 指定不同数据库模式

```json
{
  "collection_name": "document_embeddings", 
  "optimize_vcluster": "compute_cluster",
  "schema": "production"
}
```

### 不同集合优化示例

```json
{
  "collection_name": "product_vectors",
  "optimize_vcluster": "optimization_cluster"
}
```

```json
{
  "collection_name": "knowledge_base_vectors",
  "optimize_vcluster": "high_performance_cluster"
}
```

**注意**: 所有连接参数（用户名、密码、实例、工作空间、模式等）都从插件提供商配置中获取，确保配置的安全性和一致性。

## 工作流程

1. **连接验证**: 验证连接参数和权限
2. **模式验证**: 使用 `desc schema` 命令验证数据库模式是否存在
3. **获取当前集群**: 执行 `select current_vcluster()` 获取当前虚拟集群名称
4. **集群验证**: 使用 `desc vcluster` 命令验证优化集群
   - 检查集群是否存在
   - 验证集群类型为 `GENERAL`
   - 确认集群状态为 `RUNNING` 或 `SUSPENDED`
5. **集群切换**: 执行 `use vcluster optimize_cluster` 切换到优化集群
6. **优化执行**: 运行 `optimize schema.collection_name` 命令
7. **集群恢复**: 执行 `use vcluster original_cluster` 切换回原始集群
8. **结果报告**: 输出优化结果和状态信息

## 最佳实践

### 1. 集群选择
- **必须使用通用类型(GENERAL)的虚拟集群**，其他类型（如COMPUTE、STREAM等）无效
- 使用专门的计算集群进行优化
- 确保优化集群有足够的计算资源
- 避免在高峰期使用生产集群进行优化

### 2. 时间安排
- 在业务低峰期执行优化
- 大型集合优化可能需要较长时间
- 建议定期执行，而非频繁优化

### 3. 监控优化效果
- 优化前后对比查询性能
- 监控存储空间使用情况
- 跟踪索引重建效果

## 错误处理

工具包含完善的错误处理机制：

1. **参数验证**: 检查必需参数是否提供
2. **连接错误**: 处理网络和认证问题
3. **集群切换失败**: 自动尝试恢复原始集群
4. **优化命令失败**: 提供详细的错误信息

## 输出示例

### 成功输出
```
开始优化向量集合：document_embeddings
当前集群：default_ap
验证优化集群：compute_cluster
✓ 优化集群验证通过：compute_cluster (类型: GENERAL, 状态: RUNNING)
✓ 已切换到优化集群：compute_cluster
✓ 向量集合优化命令已执行
✓ 已切换回原集群：default_ap

向量集合优化完成！
- 集合名称：dify.document_embeddings
- 优化集群：compute_cluster (GENERAL)
- 当前集群：default_ap
- 状态：成功
```

### 集群验证失败输出
```
开始优化向量集合：document_embeddings
验证优化集群：special_cluster
❌ 优化集群类型不正确：COMPUTE，需要GENERAL类型
```

### 模式验证失败输出
```
开始优化向量集合：document_embeddings
验证数据库模式：production
❌ 数据库模式不存在：production
```

### JSON响应（成功）
```json
{
  "success": true,
  "collection_name": "document_embeddings",
  "schema": "dify",
  "optimize_vcluster": "compute_cluster",
  "optimize_vcluster_type": "GENERAL",
  "optimize_vcluster_state": "RUNNING",
  "original_vcluster": "default_ap",
  "message": "向量集合优化成功完成"
}
```

### JSON响应（失败）
```json
{
  "success": false,
  "error": "优化集群类型不正确：COMPUTE，需要GENERAL类型",
  "collection_name": "document_embeddings",
  "optimize_vcluster": "special_cluster"
}
```

### JSON响应（模式不存在）
```json
{
  "success": false,
  "error": "数据库模式不存在：production",
  "collection_name": "document_embeddings",
  "optimize_vcluster": "compute_cluster"
}
```

## 注意事项

1. **集群类型要求**: OPTIMIZE命令必须在通用型(GENERAL)虚拟集群中运行，其他类型集群（如COMPUTE、STREAM、REALTIME等）不会生效且会被拒绝
2. **权限要求**: 确保用户有权限访问指定的虚拟集群
3. **资源消耗**: 优化过程会消耗计算资源，建议合理安排
4. **数据安全**: 优化过程不会删除数据，但建议做好备份
5. **并发限制**: 避免同时优化多个大型集合

## 故障排除

### 常见问题

1. **集群验证失败**
   - 错误：`优化集群不存在`
     - 检查集群名称拼写是否正确
     - 确认集群已创建且可访问
   
   - 错误：`优化集群类型不正确：COMPUTE，需要GENERAL类型`
     - OPTIMIZE命令必须在GENERAL类型的虚拟集群中运行
     - 使用 `desc vcluster cluster_name` 检查集群类型
     - 选择或创建GENERAL类型的集群
   
   - 错误：`优化集群状态不可用：ERROR`
     - 集群状态必须为RUNNING或SUSPENDED
     - 联系管理员检查集群健康状态

2. **集群切换失败**
   - 检查集群名称是否正确
   - 验证用户权限
   - 确认集群状态正常

3. **优化命令超时**
   - 增加命令超时时间
   - 检查集群资源是否充足
   - 考虑分批优化大型集合

4. **无法恢复原集群**
   - 手动执行 `use vcluster original_cluster_name`
   - 检查网络连接
   - 联系管理员协助

### 日志分析

优化过程中的关键日志：
- 集群切换日志
- 优化命令执行日志  
- 性能指标变化
- 错误和警告信息

通过这些日志可以分析优化效果和排查问题。