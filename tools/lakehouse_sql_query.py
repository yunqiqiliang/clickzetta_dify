from collections.abc import Generator
from typing import Any, Dict, List
import pandas as pd
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.lakehouse_connection import LakehouseConnection

class LakehouseSQLQueryTool(Tool):
    """Clickzetta Lakehouse SQL 查询工具"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取参数
        query = tool_parameters.get("query", "").strip()
        max_rows = tool_parameters.get("max_rows", 100)
        timeout = tool_parameters.get("timeout", 120)
        
        if not query:
            yield self.create_text_message("错误：查询语句不能为空")
            return
        
        # 获取连接配置
        config = self._get_connection_config(tool_parameters)
        
        try:
            # 获取连接
            conn_manager = LakehouseConnection()
            connection = conn_manager.get_connection(config)
            
            # 执行查询
            with connection.cursor() as cursor:
                # 设置查询超时
                if timeout:
                    cursor.execute(query, parameters={'hints': {'sdk.job.timeout': timeout}})
                else:
                    cursor.execute(query)
                
                # 获取查询结果
                if cursor.description:  # 有返回结果的查询
                    columns = [desc[0] for desc in cursor.description]
                    
                    # 获取指定行数的数据
                    rows = []
                    for i in range(max_rows):
                        row = cursor.fetchone()
                        if row is None:
                            break
                        rows.append(row)
                    
                    # 转换为 DataFrame 便于处理
                    df = pd.DataFrame(rows, columns=columns)
                    
                    # 统计信息
                    total_rows = len(rows)
                    has_more = cursor.fetchone() is not None
                    
                    # 生成结果消息
                    result = {
                        "success": True,
                        "columns": columns,
                        "row_count": total_rows,
                        "has_more_rows": has_more,
                        "data": df.to_dict(orient='records'),
                        "query": query
                    }
                    
                    # 如果数据量大，同时提供表格形式的预览
                    if total_rows > 0:
                        preview_text = f"查询成功，返回 {total_rows} 行数据"
                        if has_more:
                            preview_text += f"（还有更多数据，已限制最多 {max_rows} 行）"
                        preview_text += f"\n\n{df.head(10).to_string()}"
                        if total_rows > 10:
                            preview_text += f"\n... 还有 {total_rows - 10} 行数据"
                        
                        yield self.create_text_message(preview_text)
                    
                    yield self.create_json_message(result)
                    
                else:  # 没有返回结果的查询（如 DDL）
                    yield self.create_text_message(f"查询执行成功：{query}")
                    yield self.create_json_message({
                        "success": True,
                        "message": "Query executed successfully",
                        "query": query
                    })
                    
        except Exception as e:
            error_msg = f"查询执行失败：{str(e)}"
            yield self.create_text_message(error_msg)
            yield self.create_json_message({
                "success": False,
                "error": str(e),
                "query": query
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