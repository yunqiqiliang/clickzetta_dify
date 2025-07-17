from collections.abc import Generator
from typing import Any, Dict, List, Optional
import json
import pandas as pd

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.lakehouse_connection import LakehouseConnection

class VectorSearchTool(Tool):
    """向量相似度搜索工具"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取参数
        collection_name = tool_parameters.get("collection_name", "").strip()
        query_vectors = tool_parameters.get("query_vectors", "")
        top_k = tool_parameters.get("top_k", 10)
        metric_type = tool_parameters.get("metric_type", "cosine").lower()
        filter_expr = tool_parameters.get("filter_expr", "")
        output_fields = tool_parameters.get("output_fields", "")
        
        if not collection_name:
            yield self.create_text_message("错误：集合名称不能为空")
            return
        
        if not query_vectors:
            yield self.create_text_message("错误：查询向量不能为空")
            return
        
        # 解析查询向量
        try:
            if isinstance(query_vectors, str):
                query_vectors = json.loads(query_vectors)
            
            # 支持单个向量或多个向量
            if not isinstance(query_vectors[0], list):
                query_vectors = [query_vectors]
            
            query_count = len(query_vectors)
            
        except Exception as e:
            yield self.create_text_message(f"错误：解析查询向量失败 - {str(e)}")
            return
        
        # 确定返回的字段 (与dify主项目保持一致)
        if output_fields:
            select_fields = f"id, page_content, {output_fields}, metadata"
        else:
            select_fields = "id, page_content, metadata"
        
        # 获取连接配置
        config = self._get_connection_config(tool_parameters)
        schema = config.get("schema", "public")
        
        try:
            # 获取连接
            conn_manager = LakehouseConnection()
            connection = conn_manager.get_connection(config)
            
            all_results = []
            
            with connection.cursor() as cursor:
                for idx, query_vector in enumerate(query_vectors):
                    # 构建向量搜索查询 (与dify主项目保持一致)
                    vector_str = f"VECTOR({','.join(map(str, query_vector))})"
                    distance_func = self._get_distance_function(metric_type)
                    
                    # 基础查询
                    query = f"""
                    SELECT {select_fields},
                           {distance_func}(vector, {vector_str}) AS distance
                    FROM {schema}.{collection_name}
                    """
                    
                    # 添加过滤条件
                    if filter_expr:
                        # 处理元数据字段的过滤
                        # 例如：metadata['category'] = 'electronics'
                        query += f" WHERE {filter_expr}"
                    
                    # 添加排序和限制
                    query += f"""
                    ORDER BY distance
                    LIMIT {top_k}
                    """
                    
                    cursor.execute(query)
                    
                    # 获取结果
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    
                    # 转换结果
                    query_results = []
                    for row in rows:
                        result = {}
                        for i, col in enumerate(columns):
                            if col == 'metadata' and row[i]:
                                # 解析 JSON 元数据
                                try:
                                    result[col] = json.loads(row[i]) if isinstance(row[i], str) else row[i]
                                except:
                                    result[col] = row[i]
                            else:
                                result[col] = row[i]
                        query_results.append(result)
                    
                    all_results.append({
                        "query_index": idx,
                        "results": query_results
                    })
            
            # 生成结果
            total_results = sum(len(r["results"]) for r in all_results)
            
            # 文本预览
            preview_text = f"搜索完成，共执行 {query_count} 个查询\n"
            preview_text += f"总共找到 {total_results} 个结果\n\n"
            
            for query_result in all_results[:2]:  # 只显示前两个查询的结果
                idx = query_result["query_index"]
                results = query_result["results"]
                preview_text += f"查询 {idx + 1} 的结果（前 3 个）：\n"
                
                for i, res in enumerate(results[:3]):
                    preview_text += f"  {i+1}. ID: {res['id']}, 距离: {res['distance']:.4f}\n"
                    if 'metadata' in res and res['metadata']:
                        preview_text += f"     元数据: {json.dumps(res['metadata'], ensure_ascii=False)}\n"
                preview_text += "\n"
            
            if query_count > 2:
                preview_text += f"... 还有 {query_count - 2} 个查询的结果"
            
            yield self.create_text_message(preview_text)
            
            yield self.create_json_message({
                "success": True,
                "collection_name": collection_name,
                "query_count": query_count,
                "top_k": top_k,
                "metric_type": metric_type,
                "total_results": total_results,
                "results": all_results
            })
            
        except Exception as e:
            error_msg = f"向量搜索失败：{str(e)}"
            yield self.create_text_message(error_msg)
            yield self.create_json_message({
                "success": False,
                "error": str(e),
                "collection_name": collection_name
            })
    
    def _get_distance_function(self, metric: str) -> str:
        """获取距离计算函数"""
        if metric == "l2":
            return "L2_DISTANCE"
        elif metric == "cosine":
            return "COSINE_DISTANCE"
        else:
            raise ValueError(f"不支持的距离度量：{metric}。支持的选项：l2, cosine")
    
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