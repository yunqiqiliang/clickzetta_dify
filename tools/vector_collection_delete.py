from collections.abc import Generator
from typing import Any, Dict
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.lakehouse_connection import LakehouseConnection
from tools.vector_tool_mixin import VectorToolMixin

class VectorCollectionDeleteTool(Tool, VectorToolMixin):
    """删除向量集合工具"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取参数
        collection_name = tool_parameters.get("collection_name", "").strip()
        confirm = tool_parameters.get("confirm", False)
        
        if not collection_name:
            yield self.create_text_message("错误：集合名称不能为空")
            return
        
        if not confirm:
            yield self.create_text_message("错误：请设置 confirm 参数为 true 以确认删除操作")
            yield self.create_json_message({
                "success": False,
                "error": "Deletion not confirmed",
                "collection_name": collection_name
            })
            return
        
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
                        "error": f"数据库模式不存在：{schema}",
                        "collection_name": collection_name
                    })
                    return
                
                # 首先检查表是否存在
                cursor.execute(f"SHOW TABLES IN {schema} LIKE '{collection_name}'")
                tables = cursor.fetchall()
                
                if not tables:
                    yield self.create_text_message(f"向量集合 '{collection_name}' 不存在")
                    yield self.create_json_message({
                        "success": False,
                        "error": "Collection not found",
                        "collection_name": collection_name
                    })
                    return
                
                # 获取表的向量索引信息（用于后续显示）
                index_info = []
                try:
                    cursor.execute(f"SHOW INDEX FROM {schema}.{collection_name}")
                    indexes = cursor.fetchall()
                    for idx in indexes:
                        index_str = str(idx).lower()
                        if 'vector' in index_str:
                            index_info.append(idx)
                except:
                    pass
                
                # 获取表的记录数（删除前）
                record_count = 0
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {schema}.{collection_name}")
                    count_result = cursor.fetchone()
                    record_count = count_result[0] if count_result else 0
                except:
                    pass
                
                # 执行删除操作
                drop_sql = f"DROP TABLE IF EXISTS {schema}.{collection_name}"
                cursor.execute(drop_sql)
                
                # 构建成功消息
                success_msg = f"成功删除向量集合：{collection_name}\n"
                success_msg += f"- 删除的记录数：{record_count:,}\n"
                if index_info:
                    success_msg += f"- 删除的向量索引数：{len(index_info)}"
                
                yield self.create_text_message(success_msg)
                
                yield self.create_json_message({
                    "success": True,
                    "collection_name": collection_name,
                    "schema": schema,
                    "records_deleted": record_count,
                    "indexes_deleted": len(index_info)
                })
                
        except Exception as e:
            error_msg = f"删除向量集合失败：{str(e)}"
            yield self.create_text_message(error_msg)
            yield self.create_json_message({
                "success": False,
                "error": str(e),
                "collection_name": collection_name
            })
    
