#!/usr/bin/env python3
"""最终的插件测试脚本"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_plugin():
    """测试插件的完整功能"""
    print("=== Clickzetta Lakehouse Dify 插件测试 ===\n")
    
    # 1. 先测试直接连接
    print("1. 测试直接连接...")
    result = subprocess.run(
        [sys.executable, "test_simple.py"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("✗ 直接连接测试失败")
        print(result.stdout)
        print(result.stderr)
        return False
    print("✓ 直接连接测试通过\n")
    
    # 2. 测试插件是否可以启动
    print("2. 测试插件启动...")
    env = os.environ.copy()
    env['INSTALL_METHOD'] = 'local'
    
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0,
        env=env
    )
    
    # 等待插件启动
    time.sleep(2)
    
    # 检查是否有输出
    try:
        # 读取第一行（应该是配置）
        line = process.stdout.readline()
        if line:
            try:
                config = json.loads(line.strip())
                print("✓ 插件启动成功")
                print(f"  插件名称: {config.get('name', 'Unknown')}")
                print(f"  版本: {config.get('version', 'Unknown')}")
            except json.JSONDecodeError:
                print(f"✗ 无法解析插件配置: {line}")
                process.terminate()
                return False
        else:
            print("✗ 插件没有输出配置信息")
            process.terminate()
            return False
    except Exception as e:
        print(f"✗ 测试插件启动失败: {e}")
        process.terminate()
        return False
    
    # 终止插件进程
    process.terminate()
    process.wait(timeout=5)
    
    print("\n✓ 所有测试通过！")
    print("\n下一步:")
    print("1. 使用 'dify plugin package' 打包插件")
    print("2. 在 Dify 平台上安装和测试插件")
    print("3. 配置 Lakehouse 连接凭据")
    print("4. 开始使用向量数据库功能！")
    
    return True

if __name__ == "__main__":
    success = test_plugin()
    sys.exit(0 if success else 1)