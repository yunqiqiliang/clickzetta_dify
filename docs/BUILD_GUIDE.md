# ClickZetta Dify Plugin 构建指南

本文档介绍如何构建和签名 ClickZetta Dify Plugin 插件包。

## 🚀 快速开始

### 方法一：使用快速构建脚本（推荐）

```bash
# 在项目根目录执行
./build.sh
```

这会自动生成两个版本：
- `clickzetta_lakehouse.difypkg` - 无签名版本（开发环境）
- `clickzetta_lakehouse.signed.difypkg` - 签名版本（生产环境）

### 方法二：使用完整构建脚本

```bash
# 完整构建（包含详细日志和验证）
./scripts/build_and_sign.sh

# 只构建无签名版本
./scripts/build_and_sign.sh --unsigned

# 只构建签名版本
./scripts/build_and_sign.sh --signed

# 清理旧文件
./scripts/build_and_sign.sh --clean

# 查看帮助
./scripts/build_and_sign.sh --help
```

## 📋 前置要求

### 必需的软件

1. **Dify CLI**
   ```bash
   pip install dify-cli
   ```

2. **Python 3.11+**
   ```bash
   python3 --version
   ```

3. **OpenSSL**（用于签名）
   ```bash
   openssl version
   ```

### 项目结构

确保项目包含以下关键文件：
```
clickzetta_dify/
├── manifest.yaml           # 插件清单文件
├── provider/               # 提供商配置
├── tools/                  # 工具实现
├── scripts/                # 构建和签名脚本
├── build.sh               # 快速构建脚本
└── README.md              # 项目说明
```

## 🔧 手动构建步骤

如果需要手动控制构建过程：

### 1. 构建无签名版本

```bash
# 使用 Dify CLI 构建插件包
dify plugin package . -o clickzetta_lakehouse.difypkg
```

### 2. 生成密钥对（首次使用）

```bash
# 生成 RSA 密钥对
python3 scripts/sign_plugin.py generate
```

这会生成：
- `clickzetta_plugin.private.pem` - 私钥（请妥善保管）
- `clickzetta_plugin.public.pem` - 公钥

### 3. 创建签名版本

```bash
# 使用私钥签名插件包
python3 scripts/sign_plugin.py sign clickzetta_lakehouse.difypkg
```

### 4. 验证签名

```bash
# 验证签名是否正确
python3 scripts/sign_plugin.py verify clickzetta_lakehouse.signed.difypkg
```

## 📦 输出文件说明

构建完成后会生成以下文件：

### 插件包文件

- **`clickzetta_lakehouse.difypkg`** - 无签名版本
  - 适用于开发环境
  - 需要设置 `FORCE_VERIFYING_SIGNATURE=false`
  - 文件较小，构建速度快

- **`clickzetta_lakehouse.signed.difypkg`** - 签名版本
  - 适用于生产环境
  - 支持签名验证（`FORCE_VERIFYING_SIGNATURE=true`）
  - 包含数字签名信息

### 密钥文件

- **`clickzetta_plugin.private.pem`** - 私钥文件
  - ⚠️ 请妥善保管，不要泄露
  - 用于生成数字签名
  - 不应提交到代码仓库

- **`clickzetta_plugin.public.pem`** - 公钥文件
  - 用于验证签名
  - 可以安全分享

## 🔒 签名机制说明

### 签名算法
- 使用 **RSA-SHA256** 算法
- 4096位 RSA 密钥
- 符合工业标准的安全要求

### 签名内容
- 计算插件包的 SHA256 哈希值
- 使用私钥对哈希值进行签名
- 将签名信息嵌入到插件包中

### 验证过程
1. 提取插件包中的签名信息
2. 重新计算插件内容的哈希值
3. 使用公钥验证签名
4. 确保插件完整性和来源可信

## 🚀 部署和安装

### 开发环境部署

1. 配置环境变量：
   ```bash
   FORCE_VERIFYING_SIGNATURE=false
   ```

2. 使用无签名版本：
   ```
   clickzetta_lakehouse.difypkg
   ```

### 生产环境部署

1. 保持默认配置：
   ```bash
   FORCE_VERIFYING_SIGNATURE=true
   ```

2. 使用签名版本：
   ```
   clickzetta_lakehouse.signed.difypkg
   ```

### 安装步骤

1. 登录 Dify 管理后台
2. 进入 "插件" → "安装插件" 页面
3. 选择 "本地上传" 方式
4. 上传相应的 `.difypkg` 文件
5. 等待安装完成

## 🔧 故障排除

### 常见问题

1. **构建失败：`dify: command not found`**
   ```bash
   pip install dify-cli
   ```

2. **签名失败：`openssl: command not found`**
   ```bash
   # macOS
   brew install openssl
   
   # Ubuntu/Debian
   sudo apt-get install openssl
   ```

3. **权限错误：`Permission denied`**
   ```bash
   chmod +x build.sh
   chmod +x scripts/build_and_sign.sh
   ```

4. **插件上传失败：签名验证错误**
   - 检查是否使用了正确的插件包版本
   - 确认环境变量 `FORCE_VERIFYING_SIGNATURE` 设置正确

### 调试技巧

1. **查看详细构建日志**：
   ```bash
   ./scripts/build_and_sign.sh
   ```

2. **验证插件包内容**：
   ```bash
   unzip -l clickzetta_lakehouse.difypkg
   ```

3. **检查签名信息**：
   ```bash
   python3 scripts/sign_plugin.py verify clickzetta_lakehouse.signed.difypkg
   ```

## 📝 最佳实践

### 密钥管理

1. **私钥安全**：
   - 不要将私钥提交到代码仓库
   - 定期备份私钥文件
   - 使用权限控制保护私钥

2. **密钥轮换**：
   - 建议定期更换密钥对
   - 旧签名的插件包仍然有效

### 版本管理

1. **语义化版本**：
   - 在 `manifest.yaml` 中使用语义化版本号
   - 每次发布前更新版本号

2. **发布流程**：
   - 开发阶段使用无签名版本测试
   - 发布前生成签名版本
   - 保留历史版本的插件包

### 自动化

1. **CI/CD 集成**：
   - 可以将构建脚本集成到 CI/CD 流水线
   - 自动化测试和发布流程

2. **版本标签**：
   - 使用 Git 标签管理发布版本
   - 对应的插件包版本号

## 🆘 获取帮助

如果遇到问题，请：

1. 查看脚本输出的错误信息
2. 检查前置要求是否满足
3. 参考故障排除部分
4. 提交 Issue 到项目仓库

---

**注意**: 请确保在安全的环境中生成和存储私钥文件。