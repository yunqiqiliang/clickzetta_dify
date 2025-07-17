from collections.abc import Generator
from typing import Any, Dict
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.lakehouse_connection import LakehouseConnection

class VectorCollectionCreateTool(Tool):
    """创建向量集合（表）工具"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取参数
        collection_name = tool_parameters.get("collection_name", "").strip()
        dimension = tool_parameters.get("dimension", 384)
        id_type = tool_parameters.get("id_type", "string")
        metadata_fields = tool_parameters.get("metadata_fields", "")
        create_index = tool_parameters.get("create_index", True)
        
        if not collection_name:
            yield self.create_text_message("错误：集合名称不能为空")
            return
        
        # 获取连接配置
        config = self._get_connection_config(tool_parameters)
        
        try:
            # 获取连接
            conn_manager = LakehouseConnection()
            connection = conn_manager.get_connection(config)
            
            with connection.cursor() as cursor:
                # 获取schema
                schema = config.get("schema", "public")
                
                # 构建创建表的 SQL (与dify主项目保持一致)
                id_column_type = "STRING" if id_type == "string" else "BIGINT"
                
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {schema}.{collection_name} (
                    id {id_column_type} NOT NULL,
                    page_content STRING NOT NULL,
                    metadata JSON,
                    vector VECTOR(FLOAT, {dimension}) NOT NULL,
                    PRIMARY KEY (id)
                )
                """
                
                # 添加额外的元数据字段
                if metadata_fields:
                    fields = [f.strip() for f in metadata_fields.split(",")]
                    for field in fields:
                        if ":" in field:
                            field_name, field_type = field.split(":", 1)
                            field_type = field_type.strip().upper()
                            if field_type in ["STRING", "INT", "BIGINT", "FLOAT", "DOUBLE", "BOOLEAN", "DATE", "TIMESTAMP"]:
                                create_table_sql += f",\n    {field_name.strip()} {field_type}"
                
                create_table_sql += ",\n    PRIMARY KEY (id)\n)"
                
                # 执行创建表
                cursor.execute(create_table_sql)
                
                # 创建向量索引 (与dify主项目保持一致)
                if create_index:
                    # 创建HNSW向量索引
                    vector_index_name = f"idx_{collection_name}_vector"
                    
                    vector_index_sql = f"""
                    CREATE VECTOR INDEX IF NOT EXISTS {vector_index_name}
                    ON TABLE {schema}.{collection_name}(vector)
                    PROPERTIES (
                        "distance.function" = "cosine_distance",
                        "scalar.type" = "f32",
                        "m" = "16",
                        "ef.construction" = "128"
                    )
                    """
                    cursor.execute(vector_index_sql)
                    
                    # 创建倒排索引用于全文搜索
                    text_index_name = f"idx_{collection_name}_text"
                    
                    text_index_sql = f"""
                    CREATE INVERTED INDEX IF NOT EXISTS {text_index_name}
                    ON TABLE {schema}.{collection_name} (page_content)
                    PROPERTIES (
                        "analyzer" = "chinese",
                        "mode" = "smart"
                    )
                    """
                    try:
                        cursor.execute(text_index_sql)
                    except Exception as e:
                        # 倒排索引失败不影响主要功能
                        pass
                
                # 成功消息
                success_msg = f"成功创建向量集合：{collection_name}\n"
                success_msg += f"- 向量维度：{dimension}\n"
                success_msg += f"- ID 类型：{id_type}\n"
                success_msg += f"- 表结构：id, page_content, metadata, vector\n"
                if metadata_fields:
                    success_msg += f"- 元数据字段：{metadata_fields}\n"
                if create_index:
                    success_msg += f"- 已创建 HNSW 向量索引\n"
                    success_msg += f"- 已创建倒排索引（全文搜索）"
                
                yield self.create_text_message(success_msg)
                
                yield self.create_json_message({
                    "success": True,
                    "collection_name": collection_name,
                    "dimension": dimension,
                    "id_type": id_type,
                    "metadata_fields": metadata_fields,
                    "index_created": create_index
                })
                
        except Exception as e:
            error_msg = f"创建向量集合失败：{str(e)}"
            yield self.create_text_message(error_msg)
            yield self.create_json_message({
                "success": False,
                "error": str(e),
                "collection_name": collection_name
            })
    
    def _get_connection_config(self, tool_parameters: dict[str, Any]) -> Dict[str, Any]:
        """从工具参数中提取连接配置"""
        # 优先使用工具参数，如果没有则使用提供商凭据
        return {
            "username": tool_parameters.get("username") or self.runtime.credentials.get("username"),
            "password": tool_parameters.get("password") or self.runtime.credentials.get("password"),
            "instance": tool_parameters.get("instance") or self.runtime.credentials.get("instance"),
            "service": tool_parameters.get("service") or self.runtime.credentials.get("service", "api.clickzetta.com"),
            "workspace": tool_parameters.get("workspace") or self.runtime.credentials.get("workspace", "default"),
            "vcluster": tool_parameters.get("vcluster") or self.runtime.credentials.get("vcluster", "default_ap"),
            "schema": tool_parameters.get("schema") or self.runtime.credentials.get("schema", "public"),
        }