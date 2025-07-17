#!/usr/bin/env python3
"""测试 Lakehouse 连接"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.lakehouse_connection import LakehouseConnection

# 加载环境变量
load_dotenv()

def test_connection():
    """测试基本连接"""
    print("=== 测试 Lakehouse 连接 ===")
    
    # 获取连接配置
    config = {
        "username": os.getenv("LAKEHOUSE_USERNAME"),
        "password": os.getenv("LAKEHOUSE_PASSWORD"),
        "instance": os.getenv("LAKEHOUSE_INSTANCE"),
        "service": os.getenv("LAKEHOUSE_SERVICE"),
        "workspace": os.getenv("LAKEHOUSE_WORKSPACE"),
        "vcluster": os.getenv("LAKEHOUSE_VCLUSTER"),
        "schema": os.getenv("LAKEHOUSE_SCHEMA"),
    }
    
    print(f"连接配置:")
    print(f"  实例: {config['instance']}")
    print(f"  服务: {config['service']}")
    print(f"  工作空间: {config['workspace']}")
    print(f"  虚拟集群: {config['vcluster']}")
    print(f"  模式: {config['schema']}")
    
    try:
        # 创建连接
        conn_manager = LakehouseConnection()
        connection = conn_manager.get_connection(config)
        
        # 执行简单查询
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f"\n✓ 连接成功！测试查询结果: {result}")
            
            # 查询当前模式
            cursor.execute(f"USE SCHEMA {config['schema']}")
            cursor.execute("SELECT CURRENT_SCHEMA()")
            current_schema = cursor.fetchone()
            print(f"✓ 当前模式: {current_schema[0]}")
            
            # 显示版本信息（如果有）
            try:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"✓ Lakehouse 版本: {version[0]}")
            except:
                pass
        
        # 关闭连接
        conn_manager.close()
        print("\n✓ 连接测试完成！")
        return True
        
    except Exception as e:
        print(f"\n✗ 连接失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)