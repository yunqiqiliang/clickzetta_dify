#!/usr/bin/env python3
"""按照 Dify 方式测试插件工具"""

import os
import sys
import json
import random
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from dify_plugin import ToolRuntime, Session
from dify_plugin.entities.tool import ToolProviderCredentials
from tools.vector_collection_create import VectorCollectionCreateTool
from tools.vector_collection_list import VectorCollectionListTool
from tools.vector_insert import VectorInsertTool
from tools.vector_search import VectorSearchTool
from tools.vector_delete import VectorDeleteTool
from tools.lakehouse_sql_query import LakehouseSQLQueryTool

# 加载环境变量
load_dotenv()

class MockSession(Session):
    """模拟 Session 类"""
    def __init__(self):
        self.data = {}

class MockToolRuntime(ToolRuntime):
    """模拟 ToolRuntime 类"""
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = ToolProviderCredentials(
            credentials=credentials,
            encrypted_credentials={}
        )

def create_tool_runtime() -> ToolRuntime:
    """创建工具运行时"""
    credentials = {
        "username": os.getenv("LAKEHOUSE_USERNAME"),
        "password": os.getenv("LAKEHOUSE_PASSWORD"),
        "instance": os.getenv("LAKEHOUSE_INSTANCE"),
        "service": os.getenv("LAKEHOUSE_SERVICE"),
        "workspace": os.getenv("LAKEHOUSE_WORKSPACE"),
        "vcluster": os.getenv("LAKEHOUSE_VCLUSTER"),
        "schema": os.getenv("LAKEHOUSE_SCHEMA"),
    }
    return MockToolRuntime(credentials)

def print_tool_result(messages):
    """打印工具执行结果"""
    for msg in messages:
        if hasattr(msg, 'type'):
            if msg.type == 'text':
                print(msg.text)
            elif msg.type == 'json':
                print(json.dumps(msg.json, indent=2, ensure_ascii=False))

def generate_random_vector(dimension):
    """生成随机向量"""
    return [random.random() for _ in range(dimension)]

def test_with_dify_tools():
    """使用 Dify 方式测试工具"""
    print("=== Dify 插件工具测试 ===\n")
    
    # 创建运行时和会话
    runtime = create_tool_runtime()
    session = MockSession()
    
    # 获取基础配置
    base_config = {
        "username": os.getenv("LAKEHOUSE_USERNAME"),
        "password": os.getenv("LAKEHOUSE_PASSWORD"),
        "instance": os.getenv("LAKEHOUSE_INSTANCE"),
        "service": os.getenv("LAKEHOUSE_SERVICE"),
        "workspace": os.getenv("LAKEHOUSE_WORKSPACE"),
        "vcluster": os.getenv("LAKEHOUSE_VCLUSTER"),
        "schema": os.getenv("LAKEHOUSE_SCHEMA"),
    }
    
    collection_name = os.getenv("TEST_COLLECTION_NAME", "test_embeddings")
    dimension = int(os.getenv("TEST_VECTOR_DIMENSION", "384"))
    
    try:
        # 1. 创建向量集合
        print("\n--- 测试创建向量集合 ---")
        create_tool = VectorCollectionCreateTool(runtime, session)
        params = {
            **base_config,
            "collection_name": collection_name,
            "dimension": dimension,
            "id_type": "string",
            "metadata_fields": "title:STRING, content:STRING, category:STRING",
            "create_index": True
        }
        result = list(create_tool._invoke(params))
        print_tool_result(result)
        
        # 2. 列出向量集合
        print("\n--- 测试列出向量集合 ---")
        list_tool = VectorCollectionListTool(runtime, session)
        result = list(list_tool._invoke(base_config))
        print_tool_result(result)
        
        # 3. 插入向量
        print("\n--- 测试插入向量 ---")
        insert_tool = VectorInsertTool(runtime, session)
        vectors = [generate_random_vector(dimension) for _ in range(3)]
        params = {
            **base_config,
            "collection_name": collection_name,
            "vectors": json.dumps(vectors),
            "ids": json.dumps(["test_1", "test_2", "test_3"]),
            "metadata": json.dumps([
                {"title": "文档1", "category": "技术"},
                {"title": "文档2", "category": "产品"},
                {"title": "文档3", "category": "技术"}
            ])
        }
        result = list(insert_tool._invoke(params))
        print_tool_result(result)
        
        # 4. 向量搜索
        print("\n--- 测试向量搜索 ---")
        search_tool = VectorSearchTool(runtime, session)
        query_vector = generate_random_vector(dimension)
        params = {
            **base_config,
            "collection_name": collection_name,
            "query_vectors": json.dumps([query_vector]),
            "top_k": 3,
            "metric_type": "cosine"
        }
        result = list(search_tool._invoke(params))
        print_tool_result(result)
        
        # 5. SQL 查询
        print("\n--- 测试 SQL 查询 ---")
        sql_tool = LakehouseSQLQueryTool(runtime, session)
        params = {
            **base_config,
            "query": f"SELECT COUNT(*) as total FROM {collection_name}",
            "max_rows": 10
        }
        result = list(sql_tool._invoke(params))
        print_tool_result(result)
        
        # 6. 删除向量
        print("\n--- 测试删除向量 ---")
        delete_tool = VectorDeleteTool(runtime, session)
        params = {
            **base_config,
            "collection_name": collection_name,
            "ids": json.dumps(["test_1"])
        }
        result = list(delete_tool._invoke(params))
        print_tool_result(result)
        
        print("\n✓ 所有测试完成！")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_dify_tools()