#!/bin/bash

# ClickZetta Dify Plugin - 完整构建和签名脚本
# 该脚本将自动构建插件包并生成签名版本

set -e  # 遇到错误立即退出

# 配置变量
PLUGIN_NAME="clickzetta_lakehouse"
PROJECT_DIR="/Users/liangmo/Documents/GitHub/clickzetta_dify"
SCRIPTS_DIR="$PROJECT_DIR/scripts"
UNSIGNED_PKG="$PLUGIN_NAME.difypkg"
SIGNED_PKG="$PLUGIN_NAME.signed.difypkg"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖环境..."
    
    # 检查 dify 命令
    if ! command -v dify &> /dev/null; then
        log_error "dify 命令未找到，请先安装 Dify CLI"
        log_info "安装方法: pip install dify-cli"
        exit 1
    fi
    
    # 检查 python3
    if ! command -v python3 &> /dev/null; then
        log_error "python3 未找到"
        exit 1
    fi
    
    # 检查 openssl
    if ! command -v openssl &> /dev/null; then
        log_error "openssl 未找到，签名功能需要 openssl"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 清理旧文件
cleanup_old_files() {
    log_info "清理旧的插件包文件..."
    
    cd "$PROJECT_DIR"
    
    if [ -f "$UNSIGNED_PKG" ]; then
        rm "$UNSIGNED_PKG"
        log_info "已删除旧的无签名版本: $UNSIGNED_PKG"
    fi
    
    if [ -f "$SIGNED_PKG" ]; then
        rm "$SIGNED_PKG"
        log_info "已删除旧的签名版本: $SIGNED_PKG"
    fi
}

# 构建无签名插件包
build_unsigned_package() {
    log_info "构建无签名插件包..."
    
    cd "$PROJECT_DIR"
    
    # 使用 dify CLI 构建插件包
    if dify plugin package . -o "$UNSIGNED_PKG"; then
        log_success "无签名插件包构建完成: $UNSIGNED_PKG"
    else
        log_error "插件包构建失败"
        exit 1
    fi
    
    # 检查文件大小
    if [ -f "$UNSIGNED_PKG" ]; then
        file_size=$(ls -lh "$UNSIGNED_PKG" | awk '{print $5}')
        log_info "插件包大小: $file_size"
    else
        log_error "插件包文件未生成"
        exit 1
    fi
}

# 生成或检查密钥对
ensure_keys() {
    log_info "检查签名密钥..."
    
    cd "$PROJECT_DIR"
    
    local private_key="clickzetta_plugin.private.pem"
    local public_key="clickzetta_plugin.public.pem"
    
    if [ ! -f "$private_key" ] || [ ! -f "$public_key" ]; then
        log_warning "签名密钥不存在，正在生成新的密钥对..."
        
        if python3 "$SCRIPTS_DIR/sign_plugin.py" generate; then
            log_success "密钥对生成完成"
        else
            log_error "密钥对生成失败"
            exit 1
        fi
    else
        log_success "签名密钥已存在"
    fi
    
    # 验证密钥文件
    if [ -s "$private_key" ] && [ -s "$public_key" ]; then
        log_info "密钥文件验证通过"
    else
        log_error "密钥文件损坏或为空"
        exit 1
    fi
}

# 生成签名版本
create_signed_package() {
    log_info "生成签名版本插件包..."
    
    cd "$PROJECT_DIR"
    
    if [ ! -f "$UNSIGNED_PKG" ]; then
        log_error "无签名版本不存在: $UNSIGNED_PKG"
        exit 1
    fi
    
    # 使用签名脚本生成签名版本
    if python3 "$SCRIPTS_DIR/sign_plugin.py" sign "$UNSIGNED_PKG"; then
        log_success "签名版本生成完成: $SIGNED_PKG"
    else
        log_error "签名生成失败"
        exit 1
    fi
    
    # 验证签名
    log_info "验证签名..."
    if python3 "$SCRIPTS_DIR/sign_plugin.py" verify "$SIGNED_PKG"; then
        log_success "签名验证通过"
    else
        log_error "签名验证失败"
        exit 1
    fi
}

# 显示结果摘要
show_summary() {
    log_info "构建摘要:"
    echo
    
    cd "$PROJECT_DIR"
    
    if [ -f "$UNSIGNED_PKG" ]; then
        unsigned_size=$(ls -lh "$UNSIGNED_PKG" | awk '{print $5}')
        echo -e "  📦 无签名版本: ${GREEN}$UNSIGNED_PKG${NC} ($unsigned_size)"
        echo -e "     用途: 开发环境 (需要设置 FORCE_VERIFYING_SIGNATURE=false)"
    fi
    
    if [ -f "$SIGNED_PKG" ]; then
        signed_size=$(ls -lh "$SIGNED_PKG" | awk '{print $5}')
        echo -e "  🔐 签名版本:   ${GREEN}$SIGNED_PKG${NC} ($signed_size)"
        echo -e "     用途: 生产环境 (FORCE_VERIFYING_SIGNATURE=true)"
    fi
    
    echo
    echo -e "${BLUE}安装方法:${NC}"
    echo "  1. 登录 Dify 管理后台"
    echo "  2. 进入 \"插件\" → \"安装插件\" 页面"
    echo "  3. 选择 \"本地上传\" 方式"
    echo "  4. 上传相应的 .difypkg 文件"
    echo
    
    echo -e "${BLUE}密钥信息:${NC}"
    if [ -f "clickzetta_plugin.public.pem" ]; then
        echo "  公钥文件: clickzetta_plugin.public.pem"
        echo "  私钥文件: clickzetta_plugin.private.pem"
        echo
        echo -e "${YELLOW}⚠️  请妥善保管私钥文件，不要泄露给他人${NC}"
    fi
}

# 主函数
main() {
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}  ClickZetta Dify Plugin 构建脚本   ${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo
    
    # 检查是否在正确的目录
    if [ ! -f "$PROJECT_DIR/manifest.yaml" ]; then
        log_error "未找到 manifest.yaml 文件，请确认脚本在正确的项目目录中运行"
        exit 1
    fi
    
    # 执行构建流程
    check_dependencies
    cleanup_old_files
    build_unsigned_package
    ensure_keys
    create_signed_package
    show_summary
    
    echo
    log_success "🎉 插件包构建和签名完成！"
}

# 帮助信息
show_help() {
    echo "ClickZetta Dify Plugin 构建和签名脚本"
    echo
    echo "用法: $0 [选项]"
    echo
    echo "选项:"
    echo "  -h, --help     显示帮助信息"
    echo "  -c, --clean    只清理旧文件，不构建"
    echo "  -u, --unsigned 只构建无签名版本"
    echo "  -s, --signed   只构建签名版本（需要先有无签名版本）"
    echo
    echo "示例:"
    echo "  $0                # 完整构建（无签名 + 签名版本）"
    echo "  $0 --clean        # 清理旧文件"
    echo "  $0 --unsigned     # 只构建无签名版本"
    echo "  $0 --signed       # 只构建签名版本"
}

# 处理命令行参数
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -c|--clean)
        log_info "执行清理操作..."
        cleanup_old_files
        log_success "清理完成"
        exit 0
        ;;
    -u|--unsigned)
        log_info "只构建无签名版本..."
        check_dependencies
        cleanup_old_files
        build_unsigned_package
        log_success "无签名版本构建完成"
        exit 0
        ;;
    -s|--signed)
        log_info "只构建签名版本..."
        cd "$PROJECT_DIR"
        if [ ! -f "$UNSIGNED_PKG" ]; then
            log_error "无签名版本不存在，请先构建无签名版本"
            exit 1
        fi
        check_dependencies
        ensure_keys
        create_signed_package
        log_success "签名版本构建完成"
        exit 0
        ;;
    "")
        # 默认执行完整构建
        main
        ;;
    *)
        log_error "未知选项: $1"
        show_help
        exit 1
        ;;
esac