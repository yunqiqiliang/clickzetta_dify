from collections.abc import Generator
from typing import Any, Dict, List
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.lakehouse_connection import LakehouseConnection

class VectorDeleteTool(Tool):
    """向量删除工具"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取参数
        collection_name = tool_parameters.get("collection_name", "").strip()
        ids = tool_parameters.get("ids", "")
        filter_expr = tool_parameters.get("filter_expr", "")
        
        if not collection_name:
            yield self.create_text_message("错误：集合名称不能为空")
            return
        
        if not ids and not filter_expr:
            yield self.create_text_message("错误：必须提供 ID 列表或过滤条件")
            return
        
        if ids and filter_expr:
            yield self.create_text_message("错误：不能同时使用 ID 列表和过滤条件")
            return
        
        # 解析 IDs
        parsed_ids = []
        if ids:
            try:
                if isinstance(ids, str):
                    ids = json.loads(ids)
                if not isinstance(ids, list):
                    ids = [ids]
                parsed_ids = ids
            except Exception as e:
                yield self.create_text_message(f"错误：解析 ID 数据失败 - {str(e)}")
                return
        
        # 获取连接配置
        config = self._get_connection_config(tool_parameters)
        schema = config.get("schema", "dify")
        
        try:
            # 获取连接
            conn_manager = LakehouseConnection()
            connection = conn_manager.get_connection(config)
            
            with connection.cursor() as cursor:
                # 首先获取要删除的记录数（用于反馈）
                if parsed_ids:
                    # 构建 ID 列表字符串
                    id_list = []
                    for id_val in parsed_ids:
                        if isinstance(id_val, str):
                            id_list.append(f"'{id_val}'")
                        else:
                            id_list.append(str(id_val))
                    
                    count_sql = f"""
                    SELECT COUNT(*) FROM {schema}.{collection_name}
                    WHERE id IN ({','.join(id_list)})
                    """
                    delete_sql = f"""
                    DELETE FROM {schema}.{collection_name}
                    WHERE id IN ({','.join(id_list)})
                    """
                else:
                    # 使用过滤条件
                    count_sql = f"""
                    SELECT COUNT(*) FROM {schema}.{collection_name}
                    WHERE {filter_expr}
                    """
                    delete_sql = f"""
                    DELETE FROM {schema}.{collection_name}
                    WHERE {filter_expr}
                    """
                
                # 获取将被删除的记录数
                cursor.execute(count_sql)
                count_result = cursor.fetchone()
                delete_count = count_result[0] if count_result else 0
                
                if delete_count == 0:
                    yield self.create_text_message("没有找到匹配的记录")
                    yield self.create_json_message({
                        "success": True,
                        "collection_name": collection_name,
                        "deleted_count": 0,
                        "message": "No matching records found"
                    })
                    return
                
                # 执行删除
                cursor.execute(delete_sql)
                
                # 成功消息
                if parsed_ids:
                    success_msg = f"成功从集合 {collection_name} 中删除 {delete_count} 个向量"
                    if delete_count < len(parsed_ids):
                        success_msg += f"\n注意：请求删除 {len(parsed_ids)} 个，实际删除 {delete_count} 个"
                else:
                    success_msg = f"成功从集合 {collection_name} 中删除 {delete_count} 个向量\n"
                    success_msg += f"使用的过滤条件：{filter_expr}"
                
                yield self.create_text_message(success_msg)
                
                yield self.create_json_message({
                    "success": True,
                    "collection_name": collection_name,
                    "deleted_count": delete_count,
                    "method": "ids" if parsed_ids else "filter",
                    "criteria": parsed_ids if parsed_ids else filter_expr
                })
                
        except Exception as e:
            error_msg = f"删除向量失败：{str(e)}"
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
            "workspace": tool_parameters.get("workspace") or self.runtime.credentials.get("workspace", "quick_start"),
            "vcluster": tool_parameters.get("vcluster") or self.runtime.credentials.get("vcluster", "default_ap"),
            "schema": tool_parameters.get("schema") or self.runtime.credentials.get("schema", "dify"),
        }