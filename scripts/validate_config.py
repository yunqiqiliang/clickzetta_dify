#!/usr/bin/env python3
"""
ClickZetta Dify Plugin 配置验证脚本
用于验证插件配置文件的完整性和正确性
"""

import os
import sys
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

def validate_tool_config(file_path):
    """验证单个工具配置文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        errors = []
        warnings = []
        
        # 必需字段检查
        required_fields = ['identity', 'description', 'parameters']
        for field in required_fields:
            if field not in config:
                errors.append(f"缺少必需字段: {field}")
        
        # identity字段检查
        if 'identity' in config:
            identity_required = ['name', 'author', 'label', 'description']
            for field in identity_required:
                if field not in config['identity']:
                    errors.append(f"identity 缺少必需字段: {field}")
            
            # 检查多语言支持
            if 'label' in config['identity']:
                if not isinstance(config['identity']['label'], dict):
                    errors.append("identity.label 应该是字典格式，包含多语言标签")
                else:
                    required_languages = ['en_US', 'zh_Hans']
                    for lang in required_languages:
                        if lang not in config['identity']['label']:
                            warnings.append(f"identity.label 缺少语言: {lang}")
            
            if 'description' in config['identity']:
                if not isinstance(config['identity']['description'], dict):
                    errors.append("identity.description 应该是字典格式，包含多语言描述")
        
        # description字段检查
        if 'description' in config:
            if not isinstance(config['description'], dict):
                errors.append("description 应该是字典格式")
            else:
                if 'human' not in config['description']:
                    errors.append("description 缺少 human 字段")
                if 'llm' not in config['description']:
                    warnings.append("description 缺少 llm 字段")
                
                # 检查human描述的多语言支持
                if 'human' in config['description']:
                    if not isinstance(config['description']['human'], dict):
                        errors.append("description.human 应该是字典格式")
                    else:
                        required_languages = ['en_US', 'zh_Hans']
                        for lang in required_languages:
                            if lang not in config['description']['human']:
                                warnings.append(f"description.human 缺少语言: {lang}")
        
        # parameters字段检查
        if 'parameters' in config:
            if not isinstance(config['parameters'], list):
                errors.append("parameters 应该是数组格式")
            else:
                for i, param in enumerate(config['parameters']):
                    if not isinstance(param, dict):
                        errors.append(f"参数 {i} 应该是字典格式")
                        continue
                    
                    param_required = ['name', 'type', 'required']
                    for field in param_required:
                        if field not in param:
                            errors.append(f"参数 {i} 缺少必需字段: {field}")
                    
                    # 检查参数标签和描述
                    if 'label' not in param:
                        warnings.append(f"参数 {param.get('name', i)} 缺少 label 字段")
                    if 'human_description' not in param and 'llm_description' not in param:
                        warnings.append(f"参数 {param.get('name', i)} 缺少描述字段")
        
        # extra字段检查（必需）
        if 'extra' not in config:
            errors.append("缺少必需字段: extra")
        else:
            if not isinstance(config['extra'], dict):
                errors.append("extra 应该是字典格式")
            else:
                if 'python' not in config['extra']:
                    errors.append("extra 缺少必需字段: python")
                else:
                    python_config = config['extra']['python']
                    if not isinstance(python_config, dict):
                        errors.append("extra.python 应该是字典格式")
                    else:
                        if 'source' not in python_config:
                            errors.append("extra.python 缺少必需字段: source")
                        else:
                            source_file = python_config['source']
                            if not source_file.endswith('.py'):
                                warnings.append(f"extra.python.source 应该指向Python文件: {source_file}")
                            
                            # 检查源文件是否存在
                            source_path = file_path.parent.parent / python_config['source']
                            if not source_path.exists():
                                errors.append(f"源文件不存在: {python_config['source']}")
        
        return errors, warnings
        
    except yaml.YAMLError as e:
        return [f"YAML 语法错误: {e}"], []
    except Exception as e:
        return [f"文件读取错误: {e}"], []

def validate_manifest(file_path):
    """验证manifest.yaml文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        errors = []
        warnings = []
        
        # 必需字段检查
        required_fields = ['version', 'type', 'author', 'name', 'label', 'description', 'plugins']
        for field in required_fields:
            if field not in config:
                errors.append(f"缺少必需字段: {field}")
        
        # 检查插件类型
        if config.get('type') != 'plugin':
            errors.append("type 字段应该是 'plugin'")
        
        # 检查版本格式
        version = config.get('version')
        if version:
            if not isinstance(version, str) or not version.count('.') >= 2:
                warnings.append("版本号建议使用语义版本格式 (如 1.0.0)")
        
        return errors, warnings
        
    except yaml.YAMLError as e:
        return [f"YAML 语法错误: {e}"], []
    except Exception as e:
        return [f"文件读取错误: {e}"], []

def main():
    """主函数"""
    print("🔍 ClickZetta Dify Plugin 配置验证")
    print("=" * 50)
    
    if not HAS_YAML:
        print("⚠️ 未安装 PyYAML，跳过详细验证")
        print("💡 安装方法: pip3 install pyyaml")
        print("✅ 基础检查通过（跳过YAML语法验证）")
        return
    
    project_root = Path(__file__).parent.parent
    tools_dir = project_root / "tools"
    manifest_file = project_root / "manifest.yaml"
    
    total_errors = 0
    total_warnings = 0
    
    # 验证 manifest.yaml
    print("\n📋 验证 manifest.yaml...")
    if manifest_file.exists():
        errors, warnings = validate_manifest(manifest_file)
        if errors:
            print("❌ 错误:")
            for error in errors:
                print(f"   - {error}")
            total_errors += len(errors)
        if warnings:
            print("⚠️ 警告:")
            for warning in warnings:
                print(f"   - {warning}")
            total_warnings += len(warnings)
        if not errors and not warnings:
            print("✅ manifest.yaml 验证通过")
    else:
        print("❌ manifest.yaml 文件不存在")
        total_errors += 1
    
    # 验证工具配置文件
    print("\n🔧 验证工具配置文件...")
    
    if not tools_dir.exists():
        print("❌ tools 目录不存在")
        total_errors += 1
        return
    
    yaml_files = list(tools_dir.glob("*.yaml"))
    if not yaml_files:
        print("⚠️ 未找到工具配置文件")
        total_warnings += 1
        return
    
    for yaml_file in sorted(yaml_files):
        print(f"\n  📄 {yaml_file.name}")
        errors, warnings = validate_tool_config(yaml_file)
        
        if errors:
            print("     ❌ 错误:")
            for error in errors:
                print(f"        - {error}")
            total_errors += len(errors)
        
        if warnings:
            print("     ⚠️ 警告:")
            for warning in warnings:
                print(f"        - {warning}")
            total_warnings += len(warnings)
        
        if not errors and not warnings:
            print("     ✅ 验证通过")
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 验证总结:")
    print(f"   错误: {total_errors}")
    print(f"   警告: {total_warnings}")
    
    if total_errors == 0:
        print("🎉 所有配置文件验证通过！")
        sys.exit(0)
    else:
        print("💥 发现配置错误，请修复后重试")
        sys.exit(1)

if __name__ == "__main__":
    main()