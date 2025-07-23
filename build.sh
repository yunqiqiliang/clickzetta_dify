#!/bin/bash

# ClickZetta Dify Plugin - 官方标准构建脚本
# 按照Dify官方插件标准构建，无需签名验证

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔧 构建 ClickZetta Dify Plugin (官方标准)...${NC}"

# 验证配置文件
echo "验证配置文件..."
if python3 scripts/simple_validate.py > /dev/null 2>&1; then
    echo "✅ 配置验证通过"
else
    echo "❌ 配置验证失败，运行详细验证："
    python3 scripts/simple_validate.py
    exit 1
fi

# 检查manifest.yaml是否符合官方标准
echo "检查官方标准配置..."
if grep -q "verified: false" manifest.yaml; then
    echo "✅ manifest.yaml 符合官方标准 (verified: false)"
else
    echo -e "${YELLOW}⚠️  建议在manifest.yaml中设置 verified: false${NC}"
fi

# 清理旧文件
echo "清理旧文件..."
rm -f *.difypkg

# 构建官方标准版本
echo "构建官方标准插件包..."
dify plugin package . -o clickzetta_lakehouse.difypkg

# 显示结果
echo
echo -e "${GREEN}✅ 构建完成！${NC}"
echo
echo "生成的文件："
ls -lh *.difypkg
echo
echo -e "${GREEN}📦 官方标准版本: clickzetta_lakehouse.difypkg${NC}"
echo "   ▶ 遵循Dify官方插件标准"
echo "   ▶ 无需签名验证配置"
echo "   ▶ 适用于所有环境"