#!/bin/bash

# ClickZetta Dify Plugin - 官方标准构建脚本
# 支持标准版本和签名版本构建

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 解析命令行参数
SIGN_MODE=false
if [[ "$1" == "--sign" ]]; then
    SIGN_MODE=true
    echo -e "${BLUE}🔧 构建 ClickZetta Dify Plugin (签名版本)...${NC}"
else
    echo -e "${BLUE}🔧 构建 ClickZetta Dify Plugin (标准版本)...${NC}"
fi

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

# 构建基础插件包
echo "构建基础插件包..."
dify plugin package . -o clickzetta_lakehouse.difypkg

if [[ "$SIGN_MODE" == "true" ]]; then
    # 签名模式：检查密钥并生成签名版本
    echo "检查签名密钥..."
    
    PRIVATE_KEY="clickzetta_server_keypair.private.pem"
    PUBLIC_KEY="clickzetta_server_keypair.public.pem"
    
    if [[ ! -f "$PRIVATE_KEY" ]]; then
        echo -e "${YELLOW}⚠️  未找到私钥文件，正在生成密钥对...${NC}"
        dify signature generate -f clickzetta_server_keypair
        echo "✅ 密钥对生成完成"
    fi
    
    echo "对插件进行签名..."
    dify signature sign clickzetta_lakehouse.difypkg -p "$PRIVATE_KEY"
    
    echo "验证签名..."
    if dify signature verify clickzetta_lakehouse.signed.difypkg -p "$PUBLIC_KEY"; then
        echo "✅ 签名验证成功"
    else
        echo -e "${RED}❌ 签名验证失败${NC}"
        exit 1
    fi
fi

# 显示结果
echo
echo -e "${GREEN}✅ 构建完成！${NC}"
echo
echo "生成的文件："
ls -lh *.difypkg
echo

if [[ "$SIGN_MODE" == "true" ]]; then
    echo -e "${GREEN}📦 标准版本: clickzetta_lakehouse.difypkg${NC}"
    echo "   ▶ 适用于禁用签名验证的环境"
    echo
    echo -e "${GREEN}🔐 签名版本: clickzetta_lakehouse.signed.difypkg${NC}"
    echo "   ▶ 适用于启用第三方签名验证的环境"
    echo "   ▶ 需要将 $PUBLIC_KEY 部署到服务器"
    echo
    echo -e "${YELLOW}📋 服务器配置说明：${NC}"
    echo "1. 上传公钥到: docker/volumes/plugin_daemon/public_keys/"
    echo "2. 配置环境变量: THIRD_PARTY_SIGNATURE_VERIFICATION_ENABLED=true"
    echo "3. 指定公钥路径: THIRD_PARTY_SIGNATURE_VERIFICATION_PUBLIC_KEYS=/app/storage/public_keys/$PUBLIC_KEY"
else
    echo -e "${GREEN}📦 标准版本: clickzetta_lakehouse.difypkg${NC}"
    echo "   ▶ 遵循Dify官方插件标准"
    echo "   ▶ 适用于禁用签名验证的环境"
    echo
    echo -e "${BLUE}💡 提示：使用 ./build.sh --sign 构建签名版本${NC}"
fi