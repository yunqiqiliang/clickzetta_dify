#!/bin/bash

# ClickZetta Dify Plugin - 快速构建脚本
# 简化版本，适合日常开发使用

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 构建 ClickZetta Dify Plugin...${NC}"

# 验证配置文件
echo "验证配置文件..."
if python3 scripts/simple_validate.py > /dev/null 2>&1; then
    echo "✅ 配置验证通过"
else
    echo "❌ 配置验证失败，运行详细验证："
    python3 scripts/simple_validate.py
    exit 1
fi

# 清理旧文件
echo "清理旧文件..."
rm -f clickzetta_lakehouse.difypkg clickzetta_lakehouse.signed.difypkg

# 构建无签名版本
echo "构建无签名版本..."
dify plugin package . -o clickzetta_lakehouse.difypkg

# 生成签名版本
echo "生成签名版本..."
python3 scripts/sign_plugin.py sign clickzetta_lakehouse.difypkg

# 显示结果
echo
echo -e "${GREEN}✅ 构建完成！${NC}"
echo
echo "生成的文件："
ls -lh *.difypkg
echo
echo "📦 无签名版本: clickzetta_lakehouse.difypkg (开发环境)"
echo "🔐 签名版本:   clickzetta_lakehouse.signed.difypkg (生产环境)"