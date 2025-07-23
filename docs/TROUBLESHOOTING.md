# ClickZetta Dify Plugin 故障排除指南

本文档记录了插件开发和部署过程中遇到的常见问题及解决方案。

## 🐛 插件加载错误

### 错误1：缺少 description 字段

**错误信息**：
```
ValueError: Error loading plugin configuration: 1 validation error for ToolProviderConfiguration
tools
  Value error, Error loading tool configuration: 'description' [type=value_error]
```

**原因**：工具配置文件缺少根级的 `description` 字段。

**解决方案**：
在工具配置YAML文件中添加 `description` 字段：
```yaml
identity:
  name: tool_name
  # ... 其他字段

description:
  human:
    en_US: Human-readable description in English
    zh_Hans: 中文的人类可读描述
  llm: Description for LLM understanding

parameters:
  # ... 参数定义
```

### 错误2：缺少 python 字段

**错误信息**：
```
ValueError: Error loading plugin configuration: 1 validation error for ToolConfigurationExtra
python
  Field required [type=missing, input_value={}, input_type=dict]
```

**原因**：工具配置文件缺少 `extra.python` 字段。

**解决方案**：
在工具配置YAML文件末尾添加：
```yaml
# ... 其他配置

extra:
  python:
    source: tools/your_tool_name.py
```

### 错误3：YAML语法错误

**错误信息**：
```
yaml.scanner.ScannerError: ...
```

**原因**：YAML文件格式不正确，如缩进错误、特殊字符等。

**解决方案**：
1. 检查YAML文件的缩进（使用空格，不要使用制表符）
2. 确保字符串中的特殊字符被正确转义
3. 使用YAML验证工具检查语法

## 🔧 构建问题

### 问题1：dify 命令未找到

**错误信息**：
```
bash: dify: command not found
```

**解决方案**：
```bash
pip install dify-cli
```

### 问题2：openssl 未找到

**错误信息**：
```
bash: openssl: command not found
```

**解决方案**：
```bash
# macOS
brew install openssl

# Ubuntu/Debian
sudo apt-get install openssl
```

### 问题3：权限被拒绝

**错误信息**：
```
Permission denied: ./build.sh
```

**解决方案**：
```bash
chmod +x build.sh
chmod +x scripts/build_and_sign.sh
```

## 🚀 部署问题

### 问题1：签名验证失败

**错误信息**：
```
plugin verification has been enabled, and the plugin you want to install has a bad signature
```

**解决方案**：
1. **开发环境**：设置环境变量
   ```bash
   FORCE_VERIFYING_SIGNATURE=false
   ```

2. **生产环境**：使用签名版本
   ```bash
   # 上传 clickzetta_lakehouse.signed.difypkg
   ```

### 问题2：插件启动失败

**症状**：插件安装后无法启动或频繁重启

**排查步骤**：
1. 检查插件日志：
   ```bash
   docker logs plugin_daemon
   ```

2. 验证配置文件：
   ```bash
   python3 scripts/simple_validate.py
   ```

3. 检查Python依赖：
   - 确保所有导入的库都在 requirements.txt 中
   - 检查Python版本兼容性

## 📋 配置检查清单

在提交插件前，请确认以下项目：

### 必需文件
- [ ] `manifest.yaml` - 插件清单
- [ ] `provider/lakehouse.yaml` - 提供商配置
- [ ] `provider/lakehouse.py` - 提供商实现
- [ ] `requirements.txt` - Python依赖

### 工具文件
对于每个工具，确保存在：
- [ ] `tools/tool_name.yaml` - 工具配置
- [ ] `tools/tool_name.py` - 工具实现

### 配置字段检查
每个工具配置文件应包含：
- [ ] `identity` 字段（name, author, label, description, icon）
- [ ] `description` 字段（human, llm）
- [ ] `parameters` 数组
- [ ] `extra.python.source` 字段

### 构建验证
- [ ] 运行 `python3 scripts/simple_validate.py` 无错误
- [ ] 运行 `./build.sh` 成功生成插件包
- [ ] 签名验证通过

## 🛠️ 调试技巧

### 1. 查看详细错误信息
```bash
# 查看插件守护进程日志
docker logs plugin_daemon -f

# 查看API容器日志
docker logs dify-api -f
```

### 2. 验证插件包内容
```bash
# 解压插件包查看内容
unzip -l clickzetta_lakehouse.difypkg

# 查看特定文件
unzip -p clickzetta_lakehouse.difypkg manifest.yaml
```

### 3. 测试单个工具
```python
# 在Python中测试工具导入
import sys
sys.path.append('tools')
from vector_collection_optimize import VectorCollectionOptimizeTool
```

### 4. 检查网络连接
```bash
# 测试到ClickZetta的连接
ping api.clickzetta.com

# 测试DNS解析
nslookup api.clickzetta.com
```

## 📞 获取帮助

如果遇到本文档未涵盖的问题：

1. **检查日志**：始终从容器日志开始排查
2. **验证配置**：使用提供的验证脚本
3. **逐步调试**：从最简单的功能开始测试
4. **查看示例**：参考其他工具的实现
5. **提交Issue**：在项目仓库中报告问题

## 🔄 版本兼容性

### Dify版本要求
- 最低版本：1.6.0
- 推荐版本：1.6.0+

### Python版本要求
- 最低版本：3.11
- 推荐版本：3.12

### 依赖库版本
详见 `requirements.txt` 文件中的具体版本要求。

---

**注意**：本文档会持续更新，记录新发现的问题和解决方案。