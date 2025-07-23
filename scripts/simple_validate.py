#!/usr/bin/env python3
"""
简化的配置验证脚本
不依赖外部库，进行基础检查
"""

import os
import sys
from pathlib import Path

def check_required_files():
    """检查必需文件是否存在"""
    project_root = Path(__file__).parent.parent
    
    required_files = [
        'manifest.yaml',
        'provider/lakehouse.yaml',
        'provider/lakehouse.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not (project_root / file).exists():
            missing_files.append(file)
    
    return missing_files

def check_tool_files():
    """检查工具文件的配对"""
    project_root = Path(__file__).parent.parent
    tools_dir = project_root / "tools"
    
    if not tools_dir.exists():
        return ["tools 目录不存在"]
    
    yaml_files = list(tools_dir.glob("*.yaml"))
    py_files = list(tools_dir.glob("*.py"))
    
    issues = []
    
    # 检查每个yaml文件是否有对应的py文件
    for yaml_file in yaml_files:
        if yaml_file.name == "lakehouse_connection.py":
            continue  # 这是共享文件，跳过
            
        py_file = yaml_file.with_suffix('.py')
        if not py_file.exists():
            issues.append(f"工具 {yaml_file.name} 缺少对应的Python文件")
    
    # 检查基本的yaml格式（通过查找关键字段）
    for yaml_file in yaml_files:
        if yaml_file.name.startswith('.'):
            continue
            
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_keywords = ['identity:', 'description:', 'parameters:', 'extra:', 'python:', 'source:']
            missing_keywords = []
            
            for keyword in required_keywords:
                if keyword not in content:
                    missing_keywords.append(keyword)
            
            if missing_keywords:
                issues.append(f"{yaml_file.name} 缺少关键字段: {', '.join(missing_keywords)}")
                
        except Exception as e:
            issues.append(f"读取 {yaml_file.name} 失败: {e}")
    
    return issues

def main():
    """主函数"""
    print("🔍 ClickZetta Dify Plugin 简化验证")
    print("=" * 50)
    
    total_issues = 0
    
    # 检查必需文件
    print("\n📁 检查必需文件...")
    missing_files = check_required_files()
    if missing_files:
        print("❌ 缺少文件:")
        for file in missing_files:
            print(f"   - {file}")
        total_issues += len(missing_files)
    else:
        print("✅ 所有必需文件存在")
    
    # 检查工具文件
    print("\n🔧 检查工具文件...")
    tool_issues = check_tool_files()
    if tool_issues:
        print("❌ 工具文件问题:")
        for issue in tool_issues:
            print(f"   - {issue}")
        total_issues += len(tool_issues)
    else:
        print("✅ 工具文件检查通过")
    
    # 总结
    print("\n" + "=" * 50)
    if total_issues == 0:
        print("🎉 简化验证通过！")
        sys.exit(0)
    else:
        print(f"💥 发现 {total_issues} 个问题")
        sys.exit(1)

if __name__ == "__main__":
    main()