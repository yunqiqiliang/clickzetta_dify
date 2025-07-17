#!/usr/bin/env python3
"""
测试更新后的clickzetta_dify工具

验证修改后的工具是否能正确创建与dify主项目一致的表结构
"""

import os
import sys
import json
import time
import uuid
from typing import List, Dict, Any
import numpy as np

# 添加工具路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

try:
    from vector_collection_create import VectorCollectionCreateTool
    from vector_insert import VectorInsertTool
    from vector_search import VectorSearchTool
    from lakehouse_connection import LakehouseConnection
except ImportError as e:
    print(f"❌ 无法导入工具: {e}")
    sys.exit(1)

class ToolsUpdateTest:
    """测试更新后的工具"""
    
    def __init__(self):
        self.test_collection = f"test_tools_{int(time.time())}"
        self.test_dimension = 1536
        
        # 模拟工具参数
        self.base_params = {
            "username": os.getenv("CLICKZETTA_USERNAME"),
            "password": os.getenv("CLICKZETTA_PASSWORD"),
            "instance": os.getenv("CLICKZETTA_INSTANCE"),
            "service": os.getenv("CLICKZETTA_SERVICE", "uat-api.clickzetta.com"),
            "workspace": os.getenv("CLICKZETTA_WORKSPACE", "quick_start"),
            "vcluster": os.getenv("CLICKZETTA_VCLUSTER", "default_ap"),
            "schema": os.getenv("CLICKZETTA_SCHEMA", "dify")
        }
        
        self.test_results = {}
    
    def test_collection_create_tool(self) -> bool:
        """测试集合创建工具"""
        print("\n🧪 测试集合创建工具...")
        
        try:
            tool = VectorCollectionCreateTool()
            
            # 设置工具参数
            params = self.base_params.copy()
            params.update({
                "collection_name": self.test_collection,
                "dimension": self.test_dimension,
                "id_type": "string",
                "metadata_fields": "",
                "create_index": True
            })
            
            # 调用工具
            messages = list(tool._invoke(params))
            
            # 检查结果
            success = False
            for msg in messages:
                if hasattr(msg, 'message') and "成功创建向量集合" in msg.message:
                    success = True
                    print(f"✅ 集合创建成功: {msg.message}")
                    break
            
            if not success:
                print(f"❌ 集合创建失败")
                for msg in messages:
                    if hasattr(msg, 'message'):
                        print(f"   错误信息: {msg.message}")
                return False
            
            # 验证表结构
            conn_manager = LakehouseConnection()
            connection = conn_manager.get_connection(self.base_params)
            
            with connection.cursor() as cursor:
                cursor.execute(f"DESC {self.base_params['schema']}.{self.test_collection}")
                columns = cursor.fetchall()
                
                # 检查字段
                field_names = [col[0] for col in columns]
                required_fields = ["id", "page_content", "metadata", "vector"]
                
                missing_fields = [field for field in required_fields if field not in field_names]
                if missing_fields:
                    print(f"❌ 缺少字段: {missing_fields}")
                    return False
                
                print("✅ 表结构验证通过")
                print(f"   字段: {', '.join(field_names)}")
            
            self.test_results['collection_create'] = True
            return True
            
        except Exception as e:
            print(f"❌ 集合创建工具测试失败: {e}")
            self.test_results['collection_create'] = False
            return False
    
    def test_vector_insert_tool(self) -> bool:
        """测试向量插入工具"""
        print("\n🧪 测试向量插入工具...")
        
        try:
            tool = VectorInsertTool()
            
            # 准备测试数据
            test_vectors = [
                np.random.random(self.test_dimension).tolist(),
                np.random.random(self.test_dimension).tolist(),
                np.random.random(self.test_dimension).tolist()
            ]
            
            test_contents = [
                "第一个测试文档：关于AI的内容",
                "第二个测试文档：关于机器学习的内容", 
                "第三个测试文档：关于深度学习的内容"
            ]
            
            test_metadata = [
                {"category": "AI", "type": "test"},
                {"category": "ML", "type": "test"},
                {"category": "DL", "type": "test"}
            ]
            
            test_ids = [f"test_{i}_{uuid.uuid4()}" for i in range(3)]
            
            # 设置工具参数
            params = self.base_params.copy()
            params.update({
                "collection_name": self.test_collection,
                "vectors": json.dumps(test_vectors),
                "content": json.dumps(test_contents),
                "metadata": json.dumps(test_metadata),
                "ids": json.dumps(test_ids),
                "auto_id": False
            })
            
            # 调用工具
            messages = list(tool._invoke(params))
            
            # 检查结果
            success = False
            for msg in messages:
                if hasattr(msg, 'message') and "成功插入" in msg.message:
                    success = True
                    print(f"✅ 向量插入成功: {msg.message}")
                    break
            
            if not success:
                print(f"❌ 向量插入失败")
                for msg in messages:
                    if hasattr(msg, 'message'):
                        print(f"   错误信息: {msg.message}")
                return False
            
            # 验证数据
            conn_manager = LakehouseConnection()
            connection = conn_manager.get_connection(self.base_params)
            
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {self.base_params['schema']}.{self.test_collection}")
                count = cursor.fetchone()[0]
                
                if count != 3:
                    print(f"❌ 数据验证失败: 期望3条，实际{count}条")
                    return False
                
                print("✅ 数据验证通过")
            
            self.test_results['vector_insert'] = True
            return True
            
        except Exception as e:
            print(f"❌ 向量插入工具测试失败: {e}")
            self.test_results['vector_insert'] = False
            return False
    
    def test_vector_search_tool(self) -> bool:
        """测试向量搜索工具"""
        print("\n🧪 测试向量搜索工具...")
        
        try:
            tool = VectorSearchTool()
            
            # 准备搜索向量
            query_vector = np.random.random(self.test_dimension).tolist()
            
            # 设置工具参数
            params = self.base_params.copy()
            params.update({
                "collection_name": self.test_collection,
                "query_vectors": json.dumps(query_vector),
                "top_k": 3,
                "metric_type": "cosine",
                "filter_expr": "",
                "output_fields": ""
            })
            
            # 调用工具
            messages = list(tool._invoke(params))
            
            # 检查结果
            success = False
            for msg in messages:
                if hasattr(msg, 'message') and "搜索完成" in msg.message:
                    success = True
                    print(f"✅ 向量搜索成功: {msg.message}")
                    break
            
            if not success:
                print(f"❌ 向量搜索失败")
                for msg in messages:
                    if hasattr(msg, 'message'):
                        print(f"   错误信息: {msg.message}")
                return False
            
            print("✅ 搜索工具验证通过")
            
            self.test_results['vector_search'] = True
            return True
            
        except Exception as e:
            print(f"❌ 向量搜索工具测试失败: {e}")
            self.test_results['vector_search'] = False
            return False
    
    def cleanup(self):
        """清理测试数据"""
        try:
            conn_manager = LakehouseConnection()
            connection = conn_manager.get_connection(self.base_params)
            
            with connection.cursor() as cursor:
                cursor.execute(f"DROP TABLE IF EXISTS {self.base_params['schema']}.{self.test_collection}")
            
            print("✅ 测试数据清理完成")
        except Exception as e:
            print(f"⚠️ 清理警告: {e}")
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📊 工具更新测试报告")
        print("="*60)
        
        passed_tests = sum(1 for result in self.test_results.values() if result)
        total_tests = len(self.test_results)
        
        print(f"测试集合: {self.test_collection}")
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {total_tests - passed_tests}")
        print(f"通过率: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 详细结果:")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result else "❌"
            print(f"  {status_icon} {test_name}: {'通过' if result else '失败'}")
        
        if passed_tests == total_tests:
            print("\n🎉 所有工具测试通过！修改后的工具与dify主项目完全兼容。")
        else:
            print(f"\n⚠️ {total_tests - passed_tests} 个工具测试失败，需要进一步调整。")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始工具更新测试")
        print("="*60)
        
        try:
            # 运行测试
            self.test_collection_create_tool()
            self.test_vector_insert_tool()
            self.test_vector_search_tool()
            
            # 生成报告
            self.generate_report()
            
        finally:
            self.cleanup()


def main():
    """主函数"""
    try:
        test = ToolsUpdateTest()
        test.run_all_tests()
        
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")


if __name__ == "__main__":
    main()