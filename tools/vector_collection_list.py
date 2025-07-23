from collections.abc import Generator
from typing import Any, Dict
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.lakehouse_connection import LakehouseConnection
from tools.vector_tool_mixin import VectorToolMixin

class VectorCollectionListTool(Tool, VectorToolMixin):
    """列出所有向量集合工具"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取连接配置
        config = self._get_connection_config(tool_parameters)
        
        try:
            # 获取连接
            conn_manager = LakehouseConnection()
            connection = conn_manager.get_connection(config)
            
            with connection.cursor() as cursor:
                # 获取schema，如果工具参数中没有指定，则使用当前schema
                schema = tool_parameters.get("schema")
                if not schema:
                    schema = self._get_current_schema(cursor)
                # 验证schema是否存在
                if not self._validate_schema(cursor, schema):
                    yield self.create_text_message(f"❌ 数据库模式不存在：{schema}")
                    yield self.create_json_message({
                        "success": False,
                        "error": f"数据库模式不存在：{schema}"
                    })
                    return
                
                # 首先获取所有表
                cursor.execute(f"SHOW TABLES IN {schema}")
                tables = cursor.fetchall()
                
                collections = []
                
                # 调试：查看SHOW TABLES返回的格式
                if tables and len(tables) > 0:
                    # 记录第一行的格式用于调试
                    first_row = tables[0]
                    # print(f"DEBUG: SHOW TABLES returned {len(first_row)} columns: {first_row}")
                
                for table_row in tables:
                    # SHOW TABLES 返回格式: schema_name, table_name, is_view, is_materialized_view, is_external, is_dynamic
                    if not table_row or len(table_row) < 2:
                        continue
                    
                    # 第二列是表名
                    table_name = table_row[1]
                    
                    # 跳过视图和物化视图
                    if len(table_row) >= 4:
                        is_view = table_row[2]
                        is_materialized_view = table_row[3]
                        if is_view == "true" or is_materialized_view == "true":
                            continue
                    
                    if not table_name:
                        continue
                    
                    # 检查这个表是否有 vector 列（与dify主项目保持一致）
                    try:
                        cursor.execute(f"SHOW COLUMNS IN {schema}.{table_name}")
                    except Exception as e:
                        # 如果查询失败，跳过这个表
                        continue
                    columns = cursor.fetchall()
                    
                    has_vector = False
                    vector_type = None
                    for col in columns:
                        # SHOW COLUMNS 返回格式: schema_name, table_name, column_name, data_type, comment
                        if len(col) >= 4 and col[2] == 'vector':  # 使用“vector”字段
                            col_type = col[3]
                            # 检查是否是VECTOR类型 (例如: "vector(float,384) not null")
                            if 'vector' in str(col_type).lower():
                                has_vector = True
                                vector_type = col_type
                                break
                    
                    if not has_vector:
                        continue
                    
                    comment = ""
                    
                    # 提取向量维度
                    dimension = None
                    if vector_type and '(' in vector_type and ')' in vector_type:
                        # 从类型字符串中提取维度，例如: "vector(float,384) not null"
                        try:
                            # 提取括号内的内容
                            params_str = vector_type[vector_type.index('(')+1:vector_type.index(')')]
                            # 分割参数，可能是 "float,384" 或 "384"
                            params = params_str.split(',')
                            # 取最后一个参数作为维度
                            dimension = int(params[-1].strip())
                        except:
                            pass
                    
                    # 获取表的记录数
                    cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table_name}")
                    count_result = cursor.fetchone()
                    row_count = count_result[0] if count_result else 0
                    
                    # 检查是否有向量索引
                    has_index = False
                    try:
                        cursor.execute(f"SHOW INDEX FROM {schema}.{table_name}")
                        index_rows = cursor.fetchall()
                        for index_row in index_rows:
                            # 检查索引名或类型中是否包含向量相关信息
                            # SHOW INDEX 返回的格式可能因版本而异
                            index_info = str(index_row).lower()
                            if 'vector' in index_info:  # 只检查vector关键字
                                has_index = True
                                break
                    except:
                        # 如果查询失败，默认为没有索引
                        pass
                    
                    collections.append({
                        "name": table_name,
                        "dimension": dimension,
                        "vector_count": row_count,
                        "has_index": has_index,
                        "description": comment
                    })
                
                # 生成结果
                if collections:
                    preview_text = f"找到 {len(collections)} 个向量集合：\n\n"
                    for coll in collections:
                        preview_text += f"• {coll['name']}\n"
                        preview_text += f"  - 向量维度：{coll['dimension'] or '未知'}\n"
                        preview_text += f"  - 向量数量：{coll['vector_count']:,}\n"
                        preview_text += f"  - 索引状态：{'已创建' if coll['has_index'] else '未创建'}\n"
                        if coll['description']:
                            preview_text += f"  - 描述：{coll['description']}\n"
                        preview_text += "\n"
                else:
                    preview_text = "未找到任何向量集合"
                
                yield self.create_text_message(preview_text)
                
                yield self.create_json_message({
                    "success": True,
                    "collections": collections,
                    "total_count": len(collections),
                    "schema": schema
                })
                
        except Exception as e:
            error_msg = f"列出向量集合失败：{str(e)}"
            yield self.create_text_message(error_msg)
            yield self.create_json_message({
                "success": False,
                "error": str(e)
            })
    
