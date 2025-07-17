# Clickzetta Lakehouse Dify 插件部署指南

本文档说明如何在生产环境中部署 Clickzetta Lakehouse 插件。

## 开发环境部署

在开发环境中，可以通过禁用签名验证来快速部署：

1. 修改 Dify 的环境配置：
   ```bash
   # 编辑 docker/.env 文件
   FORCE_VERIFYING_SIGNATURE=false
   ```

2. 打包插件：
   ```bash
   dify plugin package /path/to/clickzetta_dify -o clickzetta_lakehouse.difypkg
   ```

3. 在 Dify 界面上传插件

## 生产环境部署（需要签名）

在生产环境中，插件必须正确签名才能安装。

### 方案一：使用临时签名工具（推荐用于测试）

1. **生成密钥对**：
   ```bash
   cd /path/to/clickzetta_dify
   python sign_plugin.py generate
   ```
   这会生成：
   - `clickzetta_plugin.private.pem` - 私钥（请安全保管）
   - `clickzetta_plugin.public.pem` - 公钥

2. **打包插件**：
   ```bash
   dify plugin package . -o clickzetta_lakehouse.difypkg
   ```

3. **签名插件**：
   ```bash
   python sign_plugin.py sign clickzetta_lakehouse.difypkg
   ```
   这会生成 `clickzetta_lakehouse.signed.difypkg`

4. **验证签名**（可选）：
   ```bash
   python sign_plugin.py verify clickzetta_lakehouse.signed.difypkg
   ```

5. **配置 Dify 信任公钥**：
   需要将公钥配置到 Dify 系统中（具体配置方法待 Dify 官方文档更新）

### 方案二：申请官方签名（推荐用于生产）

1. 将插件提交到 Dify Marketplace
2. 通过官方审核后，插件会自动签名
3. 用户可以直接从 Marketplace 安装

### 方案三：企业私有签名

对于企业内部使用，可以：

1. 生成企业专用的签名密钥对
2. 将公钥部署到所有 Dify 实例
3. 使用私钥签名所有内部插件

## 客户部署建议

1. **开发/测试环境**：
   - 可以暂时设置 `FORCE_VERIFYING_SIGNATURE=false`
   - 方便快速迭代和测试

2. **生产环境**：
   - 保持 `FORCE_VERIFYING_SIGNATURE=true`（默认值）
   - 使用正确签名的插件包
   - 建议通过 Dify Marketplace 分发

3. **安全建议**：
   - 私钥必须安全保管，不要提交到代码仓库
   - 定期轮换签名密钥
   - 只信任已知来源的插件

## 签名机制说明

Dify 使用 RSA-SHA256 算法对插件进行签名：

1. 计算插件包的 SHA256 哈希值
2. 使用私钥对哈希值进行 RSA 签名
3. 将签名信息存储在插件包内的 `_signature.json` 文件中
4. 安装时，Dify 使用公钥验证签名

## 故障排除

### 问题：插件上传失败，提示需要签名验证

**解决方案**：
1. 检查 `FORCE_VERIFYING_SIGNATURE` 环境变量设置
2. 确保使用正确签名的插件包
3. 验证公钥是否已正确配置到 Dify

### 问题：签名验证失败

**可能原因**：
1. 插件包在签名后被修改
2. 使用了错误的公钥
3. 签名算法不匹配

**解决步骤**：
1. 重新签名插件
2. 验证公钥配置
3. 检查 Dify 日志获取详细错误信息

## 联系支持

如需帮助，请联系：
- Clickzetta 技术支持：support@clickzetta.com
- Dify 社区：https://github.com/langgenius/dify/discussions