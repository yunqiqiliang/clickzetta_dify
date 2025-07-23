from typing import Any, Dict

class VectorToolMixin:
    """向量工具混入类，提供通用的验证方法"""
    
    def _get_current_schema(self, cursor) -> str:
        """获取当前schema"""
        try:
            cursor.execute("select current_schema()")
            result = cursor.fetchone()
            current_schema = result[0] if result and result[0] else "dify"
            return current_schema
        except Exception as e:
            # 如果获取失败，使用默认值
            return "dify"
    
    def _validate_schema(self, cursor, schema_name: str) -> bool:
        """验证数据库模式是否存在"""
        try:
            # 执行desc schema命令
            desc_sql = f"desc schema {schema_name}"
            cursor.execute(desc_sql)
            
            # 如果没有异常，说明schema存在
            results = cursor.fetchall()
            return True
            
        except Exception as e:
            # 如果查询失败，可能是schema不存在或权限问题
            error_msg = str(e).lower()
            if "not found" in error_msg or "does not exist" in error_msg or "unknown database" in error_msg:
                return False
            else:
                # 其他错误，重新抛出
                raise e
    
    def _get_connection_config(self, tool_parameters: dict[str, Any]) -> Dict[str, Any]:
        """从工具参数中提取连接配置"""
        # 优先使用工具参数，如果没有则使用提供商凭据
        # 注意：schema现在是动态获取的，不在连接配置中设置
        return {
            "username": tool_parameters.get("username") or self.runtime.credentials.get("username"),
            "password": tool_parameters.get("password") or self.runtime.credentials.get("password"),
            "instance": tool_parameters.get("instance") or self.runtime.credentials.get("instance"),
            "service": tool_parameters.get("service") or self.runtime.credentials.get("service", "api.clickzetta.com"),
            "workspace": tool_parameters.get("workspace") or self.runtime.credentials.get("workspace", "quick_start"),
            "vcluster": tool_parameters.get("vcluster") or self.runtime.credentials.get("vcluster", "default_ap"),
        }