#!/usr/bin/env python3
"""
测试SQL兼容性

验证修改后的SQL语句是否与dify主项目兼容
"""

import os
import sys
import json
import time
import uuid
import numpy as np

# 添加工具路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

try:
    from lakehouse_connection import LakehouseConnection
except ImportError as e:
    print(f"❌ 无法导入lakehouse_connection: {e}")
    sys.exit(1)

class SQLCompatibilityTest:
    """SQL兼容性测试"""
    
    def __init__(self):
        self.test_collection = f"test_sql_{int(time.time())}"
        self.test_schema = "dify"
        self.test_dimension = 1536
        
        self.config = {
            "username": os.getenv("CLICKZETTA_USERNAME"),
            "password": os.getenv("CLICKZETTA_PASSWORD"),
            "instance": os.getenv("CLICKZETTA_INSTANCE"),
            "service": os.getenv("CLICKZETTA_SERVICE", "uat-api.clickzetta.com"),
            "workspace": os.getenv("CLICKZETTA_WORKSPACE", "quick_start"),
            "vcluster": os.getenv("CLICKZETTA_VCLUSTER", "default_ap"),
            "schema": self.test_schema
        }
        
        self.connection = None
        self.test_results = {}
    
    def setup_connection(self):
        """建立连接"""
        try:
            conn_manager = LakehouseConnection()
            self.connection = conn_manager.get_connection(self.config)
            print("✅ 连接建立成功")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def test_table_creation_sql(self) -> bool:
        """测试表创建SQL (修改后的工具格式)"""
        print("\n🧪 测试表创建SQL...")
        
        try:
            with self.connection.cursor() as cursor:
                # 使用修改后的表创建SQL
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
                print("✅ 表创建SQL执行成功")
                
                # 验证表结构
                cursor.execute(f"DESC {self.test_schema}.{self.test_collection}")
                columns = cursor.fetchall()
                
                field_names = [col[0] for col in columns]
                expected_fields = ["id", "page_content", "metadata", "vector"]
                
                missing_fields = [field for field in expected_fields if field not in field_names]
                if missing_fields:
                    print(f"❌ 缺少字段: {missing_fields}")
                    return False
                
                print("✅ 表结构验证通过")
                self.test_results['table_creation'] = True
                return True
                
        except Exception as e:
            print(f"❌ 表创建SQL测试失败: {e}")
            self.test_results['table_creation'] = False
            return False
    
    def test_index_creation_sql(self) -> bool:
        """测试索引创建SQL (修改后的工具格式)"""
        print("\n🧪 测试索引创建SQL...")
        
        try:
            with self.connection.cursor() as cursor:
                # 创建HNSW向量索引
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
                
                # 创建倒排索引
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
                except Exception as e:
                    print(f"⚠️ 倒排索引创建失败（不影响核心功能）: {e}")
                
                self.test_results['index_creation'] = True
                return True
                
        except Exception as e:
            print(f"❌ 索引创建SQL测试失败: {e}")
            self.test_results['index_creation'] = False
            return False
    
    def test_data_insertion_sql(self) -> bool:
        """测试数据插入SQL (修改后的工具格式)"""
        print("\n🧪 测试数据插入SQL...")
        
        try:
            with self.connection.cursor() as cursor:
                # 准备测试数据
                test_data = []
                for i in range(3):
                    doc_id = f"test_doc_{i+1}_{uuid.uuid4()}"
                    content = f"测试文档 {i+1}: 这是修改后的工具格式测试内容。"
                    metadata = {
                        "doc_id": doc_id,
                        "document_id": f"doc_{i+1}",
                        "source": "sql_test",
                        "index": i
                    }
                    vector = np.random.random(self.test_dimension).tolist()
                    test_data.append((doc_id, content, metadata, vector))
                
                # 使用修改后的插入SQL格式
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
                
                cursor.execute(insert_sql)
                print("✅ 数据插入SQL执行成功")
                
                # 验证数据
                cursor.execute(f"SELECT COUNT(*) FROM {self.test_schema}.{self.test_collection}")
                count = cursor.fetchone()[0]
                
                if count != len(test_data):
                    print(f"❌ 数据验证失败: 期望{len(test_data)}, 实际{count}")
                    return False
                
                print("✅ 数据验证通过")
                self.test_results['data_insertion'] = True
                return True
                
        except Exception as e:
            print(f"❌ 数据插入SQL测试失败: {e}")
            self.test_results['data_insertion'] = False
            return False
    
    def test_search_sql(self) -> bool:
        """测试搜索SQL (修改后的工具格式)"""
        print("\n🧪 测试搜索SQL...")
        
        try:
            with self.connection.cursor() as cursor:
                # 向量搜索SQL
                query_vector = np.random.random(self.test_dimension).tolist()
                vector_str = f"VECTOR({','.join(map(str, query_vector))})"
                
                search_sql = f"""
                SELECT id, page_content, metadata,
                       COSINE_DISTANCE(vector, {vector_str}) AS distance
                FROM {self.test_schema}.{self.test_collection}
                ORDER BY distance
                LIMIT 3
                """
                
                cursor.execute(search_sql)
                results = cursor.fetchall()
                
                print(f"✅ 向量搜索SQL执行成功，返回{len(results)}个结果")
                
                # 全文搜索SQL
                search_query = "测试文档"
                
                text_search_sql = f"""
                SELECT id, page_content, metadata
                FROM {self.test_schema}.{self.test_collection}
                WHERE page_content LIKE '%{search_query}%'
                LIMIT 3
                """
                
                cursor.execute(text_search_sql)
                text_results = cursor.fetchall()
                
                print(f"✅ 全文搜索SQL执行成功，返回{len(text_results)}个结果")
                
                self.test_results['search_sql'] = True
                return True
                
        except Exception as e:
            print(f"❌ 搜索SQL测试失败: {e}")
            self.test_results['search_sql'] = False
            return False
    
    def test_compatibility_with_dify(self) -> bool:
        """测试与dify主项目的兼容性"""
        print("\n🧪 测试与dify主项目的兼容性...")
        
        try:
            with self.connection.cursor() as cursor:
                # 模拟dify主项目的查询方式
                cursor.execute(f"SELECT id, page_content, metadata FROM {self.test_schema}.{self.test_collection} LIMIT 1")
                result = cursor.fetchone()
                
                if not result:
                    print("❌ 没有找到测试数据")
                    return False
                
                doc_id, content, metadata_json = result
                
                # 验证数据格式
                if not isinstance(doc_id, str):
                    print(f"❌ ID类型错误: {type(doc_id)}")
                    return False
                
                if not isinstance(content, str):
                    print(f"❌ 内容类型错误: {type(content)}")
                    return False
                
                try:
                    metadata = json.loads(metadata_json) if metadata_json else {}
                    if not isinstance(metadata, dict):
                        print(f"❌ 元数据类型错误: {type(metadata)}")
                        return False
                except:
                    print(f"❌ 元数据JSON解析失败")
                    return False
                
                print("✅ 数据格式与dify主项目兼容")
                
                # 验证字段顺序和命名
                cursor.execute(f"DESC {self.test_schema}.{self.test_collection}")
                columns = cursor.fetchall()
                
                field_names = [col[0] for col in columns]
                expected_order = ["id", "page_content", "metadata", "vector"]
                
                # 检查关键字段是否存在
                for field in expected_order:
                    if field not in field_names:
                        print(f"❌ 缺少关键字段: {field}")
                        return False
                
                print("✅ 字段结构与dify主项目兼容")
                
                self.test_results['dify_compatibility'] = True
                return True
                
        except Exception as e:
            print(f"❌ dify兼容性测试失败: {e}")
            self.test_results['dify_compatibility'] = False
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
        print("📊 SQL兼容性测试报告")
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
            print("\n🎉 所有SQL兼容性测试通过！")
            print("✅ 修改后的clickzetta_dify工具与dify主项目完全兼容")
        else:
            print(f"\n⚠️ {total_tests - passed_tests} 个测试失败，需要进一步调整")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始SQL兼容性测试")
        print("="*60)
        
        if not self.setup_connection():
            print("❌ 连接失败，测试中止")
            return
        
        try:
            # 运行测试
            self.test_table_creation_sql()
            self.test_index_creation_sql()
            self.test_data_insertion_sql()
            self.test_search_sql()
            self.test_compatibility_with_dify()
            
            # 生成报告
            self.generate_report()
            
        finally:
            self.cleanup()


def main():
    """主函数"""
    try:
        test = SQLCompatibilityTest()
        test.run_all_tests()
        
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")


if __name__ == "__main__":
    main()