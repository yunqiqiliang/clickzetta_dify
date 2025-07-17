#!/usr/bin/env python3
"""测试向量数据库操作"""

import os
import sys
import json
import random
import time
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.vector_collection_create import VectorCollectionCreateTool
from tools.vector_collection_list import VectorCollectionListTool
from tools.vector_insert import VectorInsertTool
from tools.vector_search import VectorSearchTool
from tools.vector_delete import VectorDeleteTool

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

def generate_random_vector(dimension):
    """生成随机向量"""
    return [random.random() for _ in range(dimension)]

def print_tool_result(messages):
    """打印工具执行结果"""
    for msg in messages:
        if hasattr(msg, 'type'):
            if msg.type == 'text':
                print(msg.text)
            elif msg.type == 'json':
                print(json.dumps(msg.json, indent=2, ensure_ascii=False))

def test_create_collection():
    """测试创建向量集合"""
    print("\n=== 测试创建向量集合 ===")
    
    tool = VectorCollectionCreateTool()
    config = get_test_config()
    
    params = {
        **config,
        "collection_name": os.getenv("TEST_COLLECTION_NAME", "test_embeddings"),
        "dimension": int(os.getenv("TEST_VECTOR_DIMENSION", "384")),
        "id_type": "string",
        "metadata_fields": "title:STRING, content:STRING, category:STRING, score:DOUBLE",
        "create_index": True
    }
    
    result = list(tool._invoke(params))
    print_tool_result(result)
    
    # 检查是否成功
    for msg in result:
        if hasattr(msg, 'json') and msg.json.get('success'):
            return True
    return False

def test_list_collections():
    """测试列出向量集合"""
    print("\n=== 测试列出向量集合 ===")
    
    tool = VectorCollectionListTool()
    config = get_test_config()
    
    result = list(tool._invoke(config))
    print_tool_result(result)
    
    return True

def test_insert_vectors():
    """测试插入向量"""
    print("\n=== 测试插入向量 ===")
    
    tool = VectorInsertTool()
    config = get_test_config()
    dimension = int(os.getenv("TEST_VECTOR_DIMENSION", "384"))
    
    # 生成测试数据
    vectors = [generate_random_vector(dimension) for _ in range(5)]
    ids = [f"doc_{i}" for i in range(5)]
    metadata = [
        {"title": f"文档 {i}", "content": f"这是测试文档 {i} 的内容", 
         "category": "技术" if i % 2 == 0 else "产品", "score": random.uniform(0.5, 1.0)}
        for i in range(5)
    ]
    
    params = {
        **config,
        "collection_name": os.getenv("TEST_COLLECTION_NAME", "test_embeddings"),
        "vectors": json.dumps(vectors),
        "ids": json.dumps(ids),
        "metadata": json.dumps(metadata)
    }
    
    result = list(tool._invoke(params))
    print_tool_result(result)
    
    # 检查是否成功
    for msg in result:
        if hasattr(msg, 'json') and msg.json.get('success'):
            return True
    return False

def test_vector_search():
    """测试向量搜索"""
    print("\n=== 测试向量搜索 ===")
    
    tool = VectorSearchTool()
    config = get_test_config()
    dimension = int(os.getenv("TEST_VECTOR_DIMENSION", "384"))
    
    # 生成查询向量
    query_vector = generate_random_vector(dimension)
    
    # 测试1: 基本搜索
    print("\n--- 测试基本搜索 ---")
    params = {
        **config,
        "collection_name": os.getenv("TEST_COLLECTION_NAME", "test_embeddings"),
        "query_vectors": json.dumps([query_vector]),
        "top_k": 3,
        "metric_type": "cosine"
    }
    
    result = list(tool._invoke(params))
    print_tool_result(result)
    
    # 测试2: 带过滤条件的搜索
    print("\n--- 测试带过滤的搜索 ---")
    params["filter_expr"] = "category = '技术'"
    params["output_fields"] = "title, category, score"
    
    result = list(tool._invoke(params))
    print_tool_result(result)
    
    return True

def test_delete_vectors():
    """测试删除向量"""
    print("\n=== 测试删除向量 ===")
    
    tool = VectorDeleteTool()
    config = get_test_config()
    
    # 测试1: 按ID删除
    print("\n--- 测试按ID删除 ---")
    params = {
        **config,
        "collection_name": os.getenv("TEST_COLLECTION_NAME", "test_embeddings"),
        "ids": json.dumps(["doc_0", "doc_1"])
    }
    
    result = list(tool._invoke(params))
    print_tool_result(result)
    
    # 测试2: 按条件删除
    print("\n--- 测试按条件删除 ---")
    params = {
        **config,
        "collection_name": os.getenv("TEST_COLLECTION_NAME", "test_embeddings"),
        "filter_expr": "score < 0.7"
    }
    
    result = list(tool._invoke(params))
    print_tool_result(result)
    
    return True

def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("Clickzetta Lakehouse 向量数据库功能测试")
    print("="*60)
    
    tests = [
        ("创建向量集合", test_create_collection),
        ("列出向量集合", test_list_collections),
        ("插入向量数据", test_insert_vectors),
        ("向量相似度搜索", test_vector_search),
        ("删除向量数据", test_delete_vectors),
        ("最终查看集合", test_list_collections)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            time.sleep(1)  # 避免请求过快
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ {test_name} 失败: {str(e)}")
            results.append((test_name, False))
    
    # 打印测试结果汇总
    print("\n" + "="*60)
    print("测试结果汇总:")
    print("="*60)
    
    success_count = 0
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
        if success:
            success_count += 1
    
    print(f"\n总计: {success_count}/{len(tests)} 个测试通过")
    print("="*60)
    
    return success_count == len(tests)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)