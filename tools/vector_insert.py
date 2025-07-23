from collections.abc import Generator
from typing import Any, Dict, List
import json
import uuid

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.lakehouse_connection import LakehouseConnection
from tools.vector_tool_mixin import VectorToolMixin

class VectorInsertTool(Tool, VectorToolMixin):
    """向量插入工具"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取参数
        collection_name = tool_parameters.get("collection_name", "").strip()
        vectors = tool_parameters.get("vectors", "")
        ids = tool_parameters.get("ids", "")
        metadata = tool_parameters.get("metadata", "")
        content = tool_parameters.get("content", "")  # 新增content参数
        auto_id = tool_parameters.get("auto_id", False)
        
        if not collection_name:
            yield self.create_text_message("错误：集合名称不能为空")
            return
        
        if not vectors:
            yield self.create_text_message("错误：向量数据不能为空")
            return
        
        if not content:
            yield self.create_text_message("错误：内容数据不能为空")
            return
        
        # 解析向量数据
        try:
            if isinstance(vectors, str):
                vectors = json.loads(vectors)
            
            if not isinstance(vectors, list):
                vectors = [vectors]
            
            # 确保所有向量都是列表格式
            parsed_vectors = []
            for v in vectors:
                if isinstance(v, str):
                    v = json.loads(v)
                parsed_vectors.append(v)
            
            vector_count = len(parsed_vectors)
            
        except Exception as e:
            yield self.create_text_message(f"错误：解析向量数据失败 - {str(e)}")
            return
        
        # 解析 IDs
        if ids:
            try:
                if isinstance(ids, str):
                    ids = json.loads(ids)
                if not isinstance(ids, list):
                    ids = [ids]
                if len(ids) != vector_count:
                    yield self.create_text_message(f"错误：ID 数量（{len(ids)}）与向量数量（{vector_count}）不匹配")
                    return
            except Exception as e:
                yield self.create_text_message(f"错误：解析 ID 数据失败 - {str(e)}")
                return
        elif auto_id:
            # 自动生成 UUID
            ids = [str(uuid.uuid4()) for _ in range(vector_count)]
        else:
            yield self.create_text_message("错误：必须提供 ID 或启用自动生成 ID")
            return
        
        # 解析元数据
        metadata_list = []
        if metadata:
            try:
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                
                if isinstance(metadata, dict):
                    # 单个元数据，应用到所有向量
                    metadata_list = [metadata] * vector_count
                elif isinstance(metadata, list):
                    if len(metadata) != vector_count:
                        yield self.create_text_message(f"错误：元数据数量（{len(metadata)}）与向量数量（{vector_count}）不匹配")
                        return
                    metadata_list = metadata
                else:
                    yield self.create_text_message("错误：元数据格式不正确")
                    return
            except Exception as e:
                yield self.create_text_message(f"错误：解析元数据失败 - {str(e)}")
                return
        else:
            # 没有元数据时使用空对象
            metadata_list = [{}] * vector_count
        
        # 解析content数据
        try:
            if isinstance(content, str):
                content_data = json.loads(content)
            else:
                content_data = content
            
            if not isinstance(content_data, list):
                content_data = [content_data]
            
            if len(content_data) != vector_count:
                yield self.create_text_message(f"错误：内容数量（{len(content_data)}）与向量数量（{vector_count}）不匹配")
                return
            
            content_list = content_data
            
        except Exception as e:
            yield self.create_text_message(f"错误：解析内容数据失败 - {str(e)}")
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
                
                # 构建批量插入 SQL (与dify主项目保持一致)
                values = []
                for i in range(vector_count):
                    vector_str = f"VECTOR({','.join(map(str, parsed_vectors[i]))})"
                    metadata_str = json.dumps(metadata_list[i], ensure_ascii=False).replace("'", "''")  # 转义单引号
                    content_str = str(content_list[i]).replace("'", "''")  # 转义单引号
                    
                    # 根据 ID 类型决定是否加引号
                    id_value = f"'{ids[i]}'" if isinstance(ids[i], str) else str(ids[i])
                    
                    values.append(f"({id_value}, '{content_str}', JSON '{metadata_str}', {vector_str})")
                
                insert_sql = f"""
                INSERT INTO {schema}.{collection_name} (id, page_content, metadata, vector)
                VALUES {','.join(values)}
                """
                
                cursor.execute(insert_sql)
                
                # 成功消息
                success_msg = f"成功插入 {vector_count} 个向量到集合 {collection_name}"
                if auto_id:
                    success_msg += f"\n生成的 ID: {', '.join(ids[:5])}"
                    if vector_count > 5:
                        success_msg += f"... (共 {vector_count} 个)"
                
                yield self.create_text_message(success_msg)
                
                yield self.create_json_message({
                    "success": True,
                    "collection_name": collection_name,
                    "inserted_count": vector_count,
                    "ids": ids,
                    "auto_id": auto_id
                })
                
        except Exception as e:
            error_msg = f"插入向量失败：{str(e)}"
            yield self.create_text_message(error_msg)
            yield self.create_json_message({
                "success": False,
                "error": str(e),
                "collection_name": collection_name
            })
    
