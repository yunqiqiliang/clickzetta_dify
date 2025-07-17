#!/usr/bin/env python3
"""测试 SQL 查询功能"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.lakehouse_sql_query import LakehouseSQLQueryTool

# 加载环境变量
load_dotenv()

def get_test_config():
    """获取测试配置"""
    return {
        "username": os.getenv("LAKEHOUSE_USERNAME"),
        "password": os.getenv("LAKEHOUSE_PASSWORD"),
        "instance": os.getenv("LAKEHOUSE_INSTANCE"),
        "service": os.getenv("LAKEHOUSE_SERVICE"),
        "workspace": os.getenv("LAKEHOUSE_WORKSPACE"),
        "vcluster": os.getenv("LAKEHOUSE_VCLUSTER"),
        "schema": os.getenv("LAKEHOUSE_SCHEMA"),
    }

def print_tool_result(messages):
    """打印工具执行结果"""
    for msg in messages:
        if hasattr(msg, 'type'):
            if msg.type == 'text':
                print(msg.text)
            elif msg.type == 'json':
                print(json.dumps(msg.json, indent=2, ensure_ascii=False))

def test_sql_queries():
    """测试各种 SQL 查询"""
    print("=== 测试 SQL 查询功能 ===\n")
    
    tool = LakehouseSQLQueryTool()
    config = get_test_config()
    collection_name = os.getenv("TEST_COLLECTION_NAME", "test_embeddings")
    
    # 测试查询列表
    test_queries = [
        {
            "name": "查看所有表",
            "query": "SHOW TABLES"
        },
        {
            "name": "查看表结构",
            "query": f"DESC {collection_name}"
        },
        {
            "name": "统计向量数量",
            "query": f"SELECT COUNT(*) as total_vectors FROM {collection_name}"
        },
        {
            "name": "查看元数据分布",
            "query": f"""
                SELECT category, COUNT(*) as count 
                FROM {collection_name} 
                GROUP BY category
            """
        },
        {
            "name": "查看索引信息",
            "query": f"SHOW INDEX FROM {collection_name}"
        },
        {
            "name": "向量搜索示例（使用 SQL）",
            "query": f"""
                SELECT id, title, category,
                       COSINE_DISTANCE(embedding, CAST([0.1, 0.2, 0.3] AS VECTOR(3))) as distance
                FROM {collection_name}
                WHERE category = '技术'
                ORDER BY distance
                LIMIT 5
            """
        }
    ]
    
    # 执行测试查询
    results = []
    for test in test_queries:
        print(f"\n--- {test['name']} ---")
        print(f"SQL: {test['query']}")
        
        params = {
            **config,
            "query": test['query'],
            "max_rows": 20,
            "timeout": 60
        }
        
        try:
            result = list(tool._invoke(params))
            print_tool_result(result)
            
            # 检查是否成功
            success = False
            for msg in result:
                if hasattr(msg, 'json') and 'success' in msg.json:
                    success = msg.json['success']
                    break
            
            results.append((test['name'], success))
        except Exception as e:
            print(f"错误: {str(e)}")
            results.append((test['name'], False))
    
    # 打印结果汇总
    print("\n" + "="*60)
    print("SQL 查询测试结果汇总:")
    print("="*60)
    
    success_count = 0
    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{name}: {status}")
        if success:
            success_count += 1
    
    print(f"\n总计: {success_count}/{len(test_queries)} 个查询成功")
    print("="*60)
    
    return success_count == len(test_queries)

if __name__ == "__main__":
    success = test_sql_queries()
    sys.exit(0 if success else 1)