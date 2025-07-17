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

安装和配置完成后，您可以在Dify的工作流或应用中通过可视化界面使用以下工具：

### 1. 向量集合管理

#### 创建向量集合 (vector_collection_create)
在Dify工作流中添加此工具，可视化配置以下参数：
- **集合名称**: `my_documents`
- **向量维度**: `1536`
- **ID类型**: `string`
- **元数据字段**: `title:STRING, category:STRING`
- **创建索引**: `是`

#### 列出向量集合 (vector_collection_list)
在Dify工作流中添加此工具，可视化配置：
- **数据库模式**: `dify`（可选，默认为配置中的schema）

#### 删除向量集合 (vector_collection_delete)
在Dify工作流中添加此工具，可视化配置：
- **集合名称**: `my_documents`
- **确认删除**: `勾选确认`

### 2. 向量数据操作

#### 插入向量 (vector_insert)
在Dify工作流中添加此工具，可视化配置：
- **集合名称**: `my_documents`
- **向量数据**: `[[0.1, 0.2, 0.3, ...], [0.4, 0.5, 0.6, ...]]`
- **文本内容**: `["第一个文档内容", "第二个文档内容"]`
- **元数据**: `[{"title": "文档1", "category": "技术"}, {"title": "文档2", "category": "产品"}]`
- **ID列表**: `["doc1", "doc2"]`
- **自动生成ID**: `否`

#### 搜索向量 (vector_search)
在Dify工作流中添加此工具，可视化配置：
- **集合名称**: `my_documents`
- **查询向量**: `[0.15, 0.25, 0.35, ...]`
- **返回数量**: `5`
- **距离度量**: `cosine`
- **过滤条件**: `metadata['category'] = '技术'`
- **输出字段**: `title,category`

#### 删除向量 (vector_delete)
在Dify工作流中添加此工具，可视化配置：
- **集合名称**: `my_documents`
- **要删除的ID**: `["doc1", "doc2"]`
- **过滤条件**: `metadata['category'] = '过期'`

### 3. SQL查询

#### 执行SQL查询 (lakehouse_sql_query)
在Dify工作流中添加此工具，可视化配置：
- **SQL语句**: `SELECT id, page_content, metadata FROM dify.my_documents WHERE metadata['category'] = '技术' LIMIT 10`
- **获取大小**: `1000`

## 在工作流中使用

### 1. 创建工作流
1. **新建工作流**：在Dify中点击「创建」→「工作流」
2. **添加工具节点**：
   - 从左侧节点面板拖拽「工具」节点到画布
   - 或点击「+」按钮选择「工具」
3. **选择工具**：
   - 在工具节点中点击「选择工具」
   - 找到「Clickzetta Lakehouse Tools」分组
   - 选择需要的具体工具（如「创建向量集合」）

### 2. 配置工具参数
1. **填写必需参数**：
   - 在工具节点的参数面板中填写必需参数
   - 参数支持固定值或变量引用
2. **使用变量**：
   - 可以引用上游节点的输出：`{{节点名.output.字段名}}`
   - 可以引用用户输入：`{{sys.user_input}}`
   - 可以引用上下文变量：`{{sys.query}}`

### 3. 连接工作流节点
1. **连接输入**：
   - 将上游节点的输出连接到工具节点的输入
   - 例如：文本嵌入节点的输出连接到向量插入工具
2. **处理输出**：
   - 工具节点的输出可以连接到下游节点
   - 输出包含工具返回的JSON数据和文本描述

### 4. 可视化操作步骤

#### 添加Clickzetta工具到工作流：
1. **拖拽工具节点**：从左侧工具面板拖拽「工具」到画布
2. **选择工具**：
   - 点击工具节点
   - 在右侧面板点击「选择工具」
   - 在工具列表中找到「Clickzetta Lakehouse Tools」
   - 选择具体工具（如「Insert Vectors」）
3. **配置参数**：
   - 在右侧参数面板填写工具参数
   - 参数可以是固定值或变量引用
4. **连接节点**：
   - 拖拽连接线将节点连接起来
   - 确保数据流向正确

#### 参数配置技巧：
- **使用变量**：`{{上游节点.output.字段名}}`
- **JSON数组格式**：向量和元数据需要JSON数组格式
- **字符串转换**：可以使用代码节点转换数据格式

### 5. 实际使用示例

#### 示例1：文档向量化存储工作流
```
开始 → 文档解析 → 文本分块 → 向量嵌入 → 向量插入(Clickzetta) → 结束
```

#### 示例2：智能问答工作流
```
开始 → 问题嵌入 → 向量搜索(Clickzetta) → 内容提取 → LLM问答 → 结束
```

#### 示例3：知识库管理工作流
```
开始 → 列出集合(Clickzetta) → 条件判断 → 创建集合(Clickzetta) → 结束
```

## 在应用中使用

### 1. 聊天应用
1. **启用工具**：
   - 在聊天应用的「工具」设置中启用Clickzetta工具
   - 选择需要的具体工具（建议选择搜索相关工具）
2. **用户交互**：
   - 用户可以通过自然语言触发向量搜索："帮我搜索关于AI的文档"
   - 系统会自动调用向量搜索工具并返回结果
3. **推荐工具**：
   - `vector_search` - 用于知识检索
   - `lakehouse_sql_query` - 用于数据查询

### 2. Agent应用  
1. **配置Agent权限**：
   - 为Agent配置Clickzetta工具的使用权限
   - Agent可以访问所有7个工具
2. **自动化处理**：
   - Agent可以自动判断何时使用哪个工具
   - 例如：自动创建集合、插入数据、搜索信息
3. **使用场景**：
   - 知识库管理Agent
   - 数据分析Agent
   - 智能问答Agent

### 3. 工作流应用
1. **集成到工作流**：
   - 将Clickzetta工具集成到复杂的工作流中
   - 与其他节点（如LLM、文本处理等）协同工作
2. **批量处理**：
   - 支持批量文档处理和向量化存储
   - 自动化的数据管理流程

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