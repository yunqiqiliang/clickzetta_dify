#!/usr/bin/env python3
"""运行所有测试"""

import os
import sys
import subprocess
from pathlib import Path

def run_test(test_name, test_file):
    """运行单个测试文件"""
    print(f"\n{'='*60}")
    print(f"运行测试: {test_name}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"运行测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("Clickzetta Lakehouse Dify 插件测试套件")
    print("="*60)
    
    # 检查环境变量
    required_vars = [
        "LAKEHOUSE_USERNAME",
        "LAKEHOUSE_PASSWORD",
        "LAKEHOUSE_INSTANCE",
        "LAKEHOUSE_SERVICE",
        "LAKEHOUSE_WORKSPACE",
        "LAKEHOUSE_VCLUSTER",
        "LAKEHOUSE_SCHEMA"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("错误：缺少必需的环境变量:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\n请确保 .env 文件已正确配置")
        sys.exit(1)
    
    # 测试列表
    tests = [
        ("连接测试", "test_connection.py"),
        ("向量操作测试", "test_vector_operations.py"),
        ("SQL 查询测试", "test_sql_query.py")
    ]
    
    # 运行测试
    test_dir = Path(__file__).parent
    results = []
    
    for test_name, test_file in tests:
        test_path = test_dir / test_file
        if test_path.exists():
            success = run_test(test_name, test_path)
            results.append((test_name, success))
        else:
            print(f"警告：测试文件不存在: {test_file}")
            results.append((test_name, False))
    
    # 显示结果汇总
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = 0
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n总计: {passed}/{len(tests)} 个测试通过")
    
    if passed == len(tests):
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n❌ {len(tests) - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())