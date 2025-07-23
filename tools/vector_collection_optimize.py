from collections.abc import Generator
from typing import Any, Dict
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.lakehouse_connection import LakehouseConnection
from tools.vector_tool_mixin import VectorToolMixin

class VectorCollectionOptimizeTool(Tool, VectorToolMixin):
    """优化向量集合工具"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取参数
        collection_name = tool_parameters.get("collection_name", "").strip()
        optimize_vcluster = tool_parameters.get("optimize_vcluster", "").strip()
        
        if not collection_name:
            yield self.create_text_message("错误：集合名称不能为空")
            return
            
        if not optimize_vcluster:
            yield self.create_text_message("错误：优化虚拟集群名称不能为空")
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
                
                yield self.create_text_message(f"开始优化向量集合：{collection_name}")
                
                # 步骤1：验证schema是否存在
                yield self.create_text_message(f"验证数据库模式：{schema}")
                if not self._validate_schema(cursor, schema):
                    yield self.create_text_message(f"❌ 数据库模式不存在：{schema}")
                    return
                yield self.create_text_message(f"✓ 数据库模式验证通过：{schema}")
                
                # 步骤2：获取当前vcluster
                try:
                    cursor.execute("select current_vcluster()")
                    result = cursor.fetchone()
                    current_vcluster = result[0] if result and result[0] else config.get("vcluster", "default_ap")
                    yield self.create_text_message(f"当前集群：{current_vcluster}")
                except Exception as e:
                    # 如果获取失败，使用配置中的默认值
                    current_vcluster = config.get("vcluster", "default_ap")
                    yield self.create_text_message(f"⚠️ 获取当前集群失败，使用默认值：{current_vcluster}")
                
                yield self.create_text_message(f"验证优化集群：{optimize_vcluster}")
                
                # 步骤3：验证优化集群是否存在且类型正确
                vcluster_info = self._validate_vcluster(cursor, optimize_vcluster)
                if not vcluster_info["exists"]:
                    yield self.create_text_message(f"❌ 优化集群不存在：{optimize_vcluster}")
                    return
                
                if vcluster_info["type"] != "GENERAL":
                    yield self.create_text_message(f"❌ 优化集群类型不正确：{vcluster_info['type']}，需要GENERAL类型")
                    return
                
                if vcluster_info["state"] not in ["RUNNING", "SUSPENDED"]:
                    yield self.create_text_message(f"❌ 优化集群状态不可用：{vcluster_info['state']}")
                    return
                
                yield self.create_text_message(f"✓ 优化集群验证通过：{optimize_vcluster} (类型: {vcluster_info['type']}, 状态: {vcluster_info['state']})")
                
                # 步骤4：切换到优化用的vcluster
                try:
                    use_vcluster_sql = f"use vcluster {optimize_vcluster}"
                    cursor.execute(use_vcluster_sql)
                    yield self.create_text_message(f"✓ 已切换到优化集群：{optimize_vcluster}")
                except Exception as e:
                    yield self.create_text_message(f"❌ 切换到优化集群失败：{str(e)}")
                    return
                
                # 步骤5：执行optimize命令
                try:
                    optimize_sql = f"optimize {schema}.{collection_name}"
                    cursor.execute(optimize_sql)
                    yield self.create_text_message(f"✓ 向量集合优化命令已执行")
                except Exception as e:
                    yield self.create_text_message(f"❌ 优化命令执行失败：{str(e)}")
                    # 尝试切换回原集群
                    try:
                        cursor.execute(f"use vcluster {current_vcluster}")
                    except:
                        pass
                    return
                
                # 步骤6：切换回原来的vcluster
                try:
                    cursor.execute(f"use vcluster {current_vcluster}")
                    yield self.create_text_message(f"✓ 已切换回原集群：{current_vcluster}")
                except Exception as e:
                    yield self.create_text_message(f"⚠️ 切换回原集群失败：{str(e)}")
                
                # 成功消息
                success_msg = f"向量集合优化完成！\n"
                success_msg += f"- 集合名称：{schema}.{collection_name}\n"
                success_msg += f"- 优化集群：{optimize_vcluster} ({vcluster_info['type']})\n"
                success_msg += f"- 当前集群：{current_vcluster}\n"
                success_msg += f"- 状态：成功"
                
                yield self.create_text_message(success_msg)
                
                yield self.create_json_message({
                    "success": True,
                    "collection_name": collection_name,
                    "schema": schema,
                    "optimize_vcluster": optimize_vcluster,
                    "optimize_vcluster_type": vcluster_info["type"],
                    "optimize_vcluster_state": vcluster_info["state"],
                    "original_vcluster": current_vcluster,
                    "message": "向量集合优化成功完成"
                })
                
        except Exception as e:
            error_msg = f"优化向量集合失败：{str(e)}"
            yield self.create_text_message(error_msg)
            yield self.create_json_message({
                "success": False,
                "error": str(e),
                "collection_name": collection_name,
                "optimize_vcluster": optimize_vcluster
            })
    
    def _validate_vcluster(self, cursor, vcluster_name: str) -> Dict[str, Any]:
        """验证虚拟集群是否存在且类型正确"""
        try:
            # 执行desc vcluster命令
            desc_sql = f"desc vcluster {vcluster_name}"
            cursor.execute(desc_sql)
            
            # 获取结果
            results = cursor.fetchall()
            
            if not results:
                return {"exists": False, "type": None, "state": None}
            
            # 解析结果，构建信息字典
            vcluster_info = {}
            for row in results:
                if len(row) >= 2:
                    info_name = row[0].strip('"') if row[0] else ""
                    info_value = row[1].strip('"') if row[1] else ""
                    vcluster_info[info_name] = info_value
            
            return {
                "exists": True,
                "type": vcluster_info.get("vcluster_type", "UNKNOWN"),
                "state": vcluster_info.get("state", "UNKNOWN"),
                "name": vcluster_info.get("name", vcluster_name),
                "creator": vcluster_info.get("creator", ""),
                "provision_mode": vcluster_info.get("provision_mode", ""),
                "current_vcluster_size": vcluster_info.get("current_vcluster_size", "0"),
                "auto_resume": vcluster_info.get("auto_resume", "false")
            }
            
        except Exception as e:
            # 如果查询失败，可能是集群不存在或权限问题
            error_msg = str(e).lower()
            if "not found" in error_msg or "does not exist" in error_msg:
                return {"exists": False, "type": None, "state": None, "error": str(e)}
            else:
                # 其他错误，重新抛出
                raise e
    
    def _get_connection_config(self, tool_parameters: dict[str, Any]) -> Dict[str, Any]:
        """从提供商凭据中获取连接配置"""
        # 对于optimize工具，只使用提供商凭据，schema是动态获取的
        return {
            "username": self.runtime.credentials.get("username"),
            "password": self.runtime.credentials.get("password"),
            "instance": self.runtime.credentials.get("instance"),
            "service": self.runtime.credentials.get("service", "api.clickzetta.com"),
            "workspace": self.runtime.credentials.get("workspace", "quick_start"),
            "vcluster": self.runtime.credentials.get("vcluster", "default_ap"),
        }