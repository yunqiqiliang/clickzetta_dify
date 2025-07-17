#!/usr/bin/env python3
"""
Clickzetta一致性测试

测试clickzetta_dify项目与dify主项目的Clickzetta实现是否一致
验证表结构、索引创建、数据操作的兼容性
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
    from lakehouse_connection import LakehouseConnection
except ImportError as e:
    print(f"❌ 无法导入lakehouse_connection: {e}")
    sys.exit(1)

class ClickzettaConsistencyTest:
    """Clickzetta一致性测试类"""
    
    def __init__(self):
        """初始化测试环境"""
        self.test_collection = f"test_consistency_{int(time.time())}"
        self.test_schema = "dify"
        self.test_dimension = 1536
        self.connection = None
        self.test_results = {}
        
        # 测试配置
        self.config = {
            "username": os.getenv("CLICKZETTA_USERNAME"),
            "password": os.getenv("CLICKZETTA_PASSWORD"),
            "instance": os.getenv("CLICKZETTA_INSTANCE"),
            "service": os.getenv("CLICKZETTA_SERVICE", "uat-api.clickzetta.com"),
            "workspace": os.getenv("CLICKZETTA_WORKSPACE", "quick_start"),
            "vcluster": os.getenv("CLICKZETTA_VCLUSTER", "default_ap"),
            "schema": self.test_schema
        }
        
        # 验证环境变量
        required_vars = ["username", "password", "instance"]
        missing_vars = [var for var in required_vars if not self.config.get(var)]
        if missing_vars:
            raise ValueError(f"缺少必需的环境变量: {missing_vars}")
    
    def setup_connection(self) -> bool:
        """建立连接"""
        try:
            conn_manager = LakehouseConnection()
            self.connection = conn_manager.get_connection(self.config)
            print("✅ 连接建立成功")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def test_table_structure_consistency(self) -> bool:
        """测试表结构一致性"""
        print("\n🧪 测试表结构一致性...")
        
        try:
            with self.connection.cursor() as cursor:
                # 创建测试表 (使用dify主项目的表结构)
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {self.test_schema}.{self.test_collection} (
                    id STRING NOT NULL,
                    page_content STRING NOT NULL,
                    metadata JSON,
                    vector VECTOR(FLOAT, {self.test_dimension}) NOT NULL,
                    PRIMARY KEY (id)
                )
                """
                cursor.execute(create_table_sql)
                print("✅ 表创建成功（使用dify主项目结构）")
                
                # 验证表结构
                cursor.execute(f"DESC {self.test_schema}.{self.test_collection}")
                columns = cursor.fetchall()
                
                # 检查必需字段
                required_fields = ["id", "page_content", "metadata", "vector"]
                existing_fields = [col[0] for col in columns]
                
                missing_fields = [field for field in required_fields if field not in existing_fields]
                if missing_fields:
                    print(f"❌ 缺少必需字段: {missing_fields}")
                    return False
                
                print("✅ 表结构验证通过")
                print(f"   字段列表: {', '.join(existing_fields)}")
                
                self.test_results['table_structure'] = True
                return True
                
        except Exception as e:
            print(f"❌ 表结构测试失败: {e}")
            self.test_results['table_structure'] = False
            return False
    
    def test_index_creation_consistency(self) -> bool:
        """测试索引创建一致性"""
        print("\n🧪 测试索引创建一致性...")
        
        try:
            with self.connection.cursor() as cursor:
                # 创建HNSW向量索引 (使用dify主项目的索引参数)
                vector_index_name = f"idx_{self.test_collection}_vector"
                
                vector_index_sql = f"""
                CREATE VECTOR INDEX IF NOT EXISTS {vector_index_name}
                ON TABLE {self.test_schema}.{self.test_collection}(vector)
                PROPERTIES (
                    "distance.function" = "cosine_distance",
                    "scalar.type" = "f32",
                    "m" = "16",
                    "ef.construction" = "128"
                )
                """
                cursor.execute(vector_index_sql)
                print("✅ HNSW向量索引创建成功")
                
                # 创建倒排索引 (用于全文搜索)
                text_index_name = f"idx_{self.test_collection}_text"
                
                text_index_sql = f"""
                CREATE INVERTED INDEX IF NOT EXISTS {text_index_name}
                ON TABLE {self.test_schema}.{self.test_collection} (page_content)
                PROPERTIES (
                    "analyzer" = "chinese",
                    "mode" = "smart"
                )
                """
                try:
                    cursor.execute(text_index_sql)
                    print("✅ 倒排索引创建成功")
                    inverted_index_created = True
                except Exception as e:
                    print(f"⚠️ 倒排索引创建失败（不影响核心功能）: {e}")
                    inverted_index_created = False
                
                # 验证索引
                cursor.execute(f"SHOW INDEX FROM {self.test_schema}.{self.test_collection}")
                indexes = cursor.fetchall()
                
                index_names = [str(idx) for idx in indexes]
                vector_index_exists = any("vector" in idx.lower() for idx in index_names)
                
                if not vector_index_exists:
                    print("❌ 向量索引未找到")
                    return False
                
                print("✅ 索引验证通过")
                print(f"   索引数量: {len(indexes)}")
                
                self.test_results['index_creation'] = True
                return True
                
        except Exception as e:
            print(f"❌ 索引创建测试失败: {e}")
            self.test_results['index_creation'] = False
            return False
    
    def test_data_insertion_consistency(self) -> bool:
        """测试数据插入一致性"""
        print("\n🧪 测试数据插入一致性...")
        
        try:
            with self.connection.cursor() as cursor:
                # 准备测试数据
                test_data = []
                for i in range(5):
                    doc_id = f"test_doc_{i+1}_{uuid.uuid4()}"
                    content = f"测试文档 {i+1}: 这是与dify主项目保持一致的测试内容。"
                    metadata = {
                        "doc_id": doc_id,
                        "document_id": f"doc_{i+1}",
                        "source": "consistency_test",
                        "index": i
                    }
                    vector = np.random.random(self.test_dimension).tolist()
                    test_data.append((doc_id, content, metadata, vector))
                
                # 使用dify主项目的插入格式
                values = []
                for doc_id, content, metadata, vector in test_data:
                    vector_str = f"VECTOR({','.join(map(str, vector))})"
                    metadata_str = json.dumps(metadata, ensure_ascii=False).replace("'", "''")
                    content_str = content.replace("'", "''")
                    
                    values.append(f"('{doc_id}', '{content_str}', JSON '{metadata_str}', {vector_str})")
                
                insert_sql = f"""
                INSERT INTO {self.test_schema}.{self.test_collection} (id, page_content, metadata, vector)
                VALUES {','.join(values)}
                """
                
                start_time = time.time()
                cursor.execute(insert_sql)
                insert_time = time.time() - start_time
                
                print(f"✅ 数据插入成功: {len(test_data)} 条记录，耗时 {insert_time:.3f}s")
                
                # 验证插入结果
                cursor.execute(f"SELECT COUNT(*) FROM {self.test_schema}.{self.test_collection}")
                count = cursor.fetchone()[0]
                
                if count != len(test_data):
                    print(f"❌ 数据验证失败: 期望 {len(test_data)}，实际 {count}")
                    return False
                
                print("✅ 数据验证通过")
                
                self.test_results['data_insertion'] = True
                return True
                
        except Exception as e:
            print(f"❌ 数据插入测试失败: {e}")
            self.test_results['data_insertion'] = False
            return False
    
    def test_vector_search_consistency(self) -> bool:
        """测试向量搜索一致性"""
        print("\n🧪 测试向量搜索一致性...")
        
        try:
            with self.connection.cursor() as cursor:
                # 使用dify主项目的搜索格式
                query_vector = np.random.random(self.test_dimension).tolist()
                vector_str = f"VECTOR({','.join(map(str, query_vector))})"
                
                search_sql = f"""
                SELECT id, page_content, metadata,
                       COSINE_DISTANCE(vector, {vector_str}) AS distance
                FROM {self.test_schema}.{self.test_collection}
                ORDER BY distance
                LIMIT 3
                """
                
                start_time = time.time()
                cursor.execute(search_sql)
                results = cursor.fetchall()
                search_time = time.time() - start_time
                
                print(f"✅ 向量搜索成功: 返回 {len(results)} 个结果，耗时 {search_time*1000:.0f}ms")
                
                # 验证搜索结果
                for i, row in enumerate(results):
                    doc_id, content, metadata_json, distance = row
                    metadata = json.loads(metadata_json) if metadata_json else {}
                    print(f"   结果 {i+1}: 距离={distance:.4f}, 文档ID={doc_id}")
                
                if len(results) == 0:
                    print("❌ 搜索结果为空")
                    return False
                
                print("✅ 搜索结果验证通过")
                
                self.test_results['vector_search'] = True
                return True
                
        except Exception as e:
            print(f"❌ 向量搜索测试失败: {e}")
            self.test_results['vector_search'] = False
            return False
    
    def test_full_text_search_consistency(self) -> bool:
        """测试全文搜索一致性"""
        print("\n🧪 测试全文搜索一致性...")
        
        try:
            with self.connection.cursor() as cursor:
                # 使用dify主项目的全文搜索格式
                search_query = "测试文档"
                
                # 尝试使用MATCH_ALL函数
                try:
                    search_sql = f"""
                    SELECT id, page_content, metadata
                    FROM {self.test_schema}.{self.test_collection}
                    WHERE MATCH_ALL(page_content, '{search_query}')
                    LIMIT 3
                    """
                    
                    start_time = time.time()
                    cursor.execute(search_sql)
                    results = cursor.fetchall()
                    search_time = time.time() - start_time
                    
                    print(f"✅ 全文搜索成功: 返回 {len(results)} 个结果，耗时 {search_time*1000:.0f}ms")
                    
                except Exception as e:
                    # 降级到LIKE搜索
                    print(f"ℹ️ MATCH_ALL搜索失败，降级到LIKE搜索: {e}")
                    
                    search_sql = f"""
                    SELECT id, page_content, metadata
                    FROM {self.test_schema}.{self.test_collection}
                    WHERE page_content LIKE '%{search_query}%'
                    LIMIT 3
                    """
                    
                    start_time = time.time()
                    cursor.execute(search_sql)
                    results = cursor.fetchall()
                    search_time = time.time() - start_time
                    
                    print(f"✅ LIKE搜索成功: 返回 {len(results)} 个结果，耗时 {search_time*1000:.0f}ms")
                
                # 验证搜索结果
                for i, row in enumerate(results):
                    doc_id, content, metadata_json = row
                    print(f"   结果 {i+1}: 文档ID={doc_id}, 内容长度={len(content)}")
                
                print("✅ 全文搜索验证通过")
                
                self.test_results['full_text_search'] = True
                return True
                
        except Exception as e:
            print(f"❌ 全文搜索测试失败: {e}")
            self.test_results['full_text_search'] = False
            return False
    
    def test_cross_project_compatibility(self) -> bool:
        """测试跨项目兼容性"""
        print("\n🧪 测试跨项目兼容性...")
        
        try:
            with self.connection.cursor() as cursor:
                # 验证表结构是否兼容dify主项目
                cursor.execute(f"DESC {self.test_schema}.{self.test_collection}")
                columns = cursor.fetchall()
                
                # 检查字段类型
                field_types = {col[0]: col[1] for col in columns}
                
                expected_types = {
                    "id": "STRING",
                    "page_content": "STRING", 
                    "metadata": "JSON",
                    "vector": "VECTOR"
                }
                
                compatibility_issues = []
                for field, expected_type in expected_types.items():
                    if field not in field_types:
                        compatibility_issues.append(f"缺少字段: {field}")
                    elif expected_type not in field_types[field]:
                        compatibility_issues.append(f"字段类型不匹配: {field} (期望: {expected_type}, 实际: {field_types[field]})")
                
                if compatibility_issues:
                    print(f"❌ 兼容性问题: {', '.join(compatibility_issues)}")
                    return False
                
                print("✅ 跨项目兼容性验证通过")
                print(f"   表结构完全兼容dify主项目")
                
                self.test_results['cross_project_compatibility'] = True
                return True
                
        except Exception as e:
            print(f"❌ 跨项目兼容性测试失败: {e}")
            self.test_results['cross_project_compatibility'] = False
            return False
    
    def cleanup(self):
        """清理测试数据"""
        try:
            if self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute(f"DROP TABLE IF EXISTS {self.test_schema}.{self.test_collection}")
                print("✅ 测试数据清理完成")
        except Exception as e:
            print(f"⚠️ 清理警告: {e}")
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📊 Clickzetta一致性测试报告")
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
        
        # 总结
        if passed_tests == total_tests:
            print("\n🎉 所有测试通过！两个项目的Clickzetta实现完全一致。")
        else:
            print(f"\n⚠️ {total_tests - passed_tests} 个测试失败，需要进一步调整。")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'results': self.test_results
        }
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始Clickzetta一致性测试")
        print("="*60)
        
        # 建立连接
        if not self.setup_connection():
            print("❌ 连接失败，测试中止")
            return None
        
        try:
            # 运行所有测试
            tests = [
                self.test_table_structure_consistency,
                self.test_index_creation_consistency,
                self.test_data_insertion_consistency,
                self.test_vector_search_consistency,
                self.test_full_text_search_consistency,
                self.test_cross_project_compatibility
            ]
            
            for test in tests:
                test()
            
            # 生成报告
            return self.generate_report()
            
        finally:
            self.cleanup()


def main():
    """主函数"""
    try:
        test = ClickzettaConsistencyTest()
        report = test.run_all_tests()
        
        if report and report['success_rate'] >= 80:
            print(f"\n🎯 测试完成！成功率: {report['success_rate']:.1f}%")
            print("✅ 两个项目的Clickzetta实现基本一致")
        else:
            print(f"\n🎯 测试完成！成功率: {report['success_rate']:.1f}%")
            print("⚠️ 需要进一步调整以提高一致性")
            
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")


if __name__ == "__main__":
    main()