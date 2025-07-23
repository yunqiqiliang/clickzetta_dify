#!/usr/bin/env python3
"""
测试向量集合优化工具
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.vector_collection_optimize import VectorCollectionOptimizeTool
from unittest.mock import Mock, MagicMock
import json

def test_vector_collection_optimize():
    """测试向量集合优化功能"""
    
    # 创建模拟的运行时环境
    mock_runtime = Mock()
    mock_runtime.credentials = {
        "username": "test_user",
        "password": "test_password", 
        "instance": "test_instance",
        "service": "api.clickzetta.com",
        "workspace": "test_workspace",
        "vcluster": "default_ap",
        "schema": "dify"
    }
    
    # 创建工具实例
    tool = VectorCollectionOptimizeTool()
    tool.runtime = mock_runtime
    
    # 模拟create_text_message和create_json_message方法
    def mock_create_text_message(text):
        return {"type": "text", "message": text}
    
    def mock_create_json_message(data):
        return {"type": "json", "data": data}
    
    tool.create_text_message = mock_create_text_message
    tool.create_json_message = mock_create_json_message
    
    print("=== 测试向量集合优化工具 ===")
    
    # 测试参数
    tool_parameters = {
        "collection_name": "test_collection",
        "optimize_vcluster": "optimize_cluster"
    }
    
    print(f"测试参数：{json.dumps(tool_parameters, indent=2, ensure_ascii=False)}")
    
    try:
        # 执行工具调用
        messages = list(tool._invoke(tool_parameters))
        
        print(f"\n工具执行结果：")
        for i, message in enumerate(messages):
            print(f"消息 {i+1}: {json.dumps(message, indent=2, ensure_ascii=False)}")
            
        print("\n✅ 向量集合优化工具测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()

def test_parameter_validation():
    """测试参数验证"""
    
    # 创建模拟的运行时环境
    mock_runtime = Mock()
    mock_runtime.credentials = {
        "username": "test_user",
        "password": "test_password", 
        "instance": "test_instance"
    }
    
    # 创建工具实例
    tool = VectorCollectionOptimizeTool()
    tool.runtime = mock_runtime
    
    # 模拟create_text_message方法
    def mock_create_text_message(text):
        return {"type": "text", "message": text}
    
    tool.create_text_message = mock_create_text_message
    
    print("\n=== 测试参数验证 ===")
    
    # 测试缺少集合名称
    print("1. 测试缺少集合名称")
    messages = list(tool._invoke({"optimize_vcluster": "test_cluster"}))
    print(f"结果：{messages[0]['message']}")
    
    # 测试缺少优化集群名称
    print("2. 测试缺少优化集群名称")
    messages = list(tool._invoke({"collection_name": "test_collection"}))
    print(f"结果：{messages[0]['message']}")
    
    print("✅ 参数验证测试完成")

if __name__ == "__main__":
    test_parameter_validation()
    test_vector_collection_optimize()