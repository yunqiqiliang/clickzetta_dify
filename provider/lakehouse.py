from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
import clickzetta


class LakehouseProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        验证 Lakehouse 连接凭据
        """
        try:
            # 检查必需的凭据字段
            required_fields = ["username", "password", "instance", "service", 
                             "workspace", "vcluster", "schema"]
            
            for field in required_fields:
                if not credentials.get(field):
                    raise ToolProviderCredentialValidationError(
                        f"Missing required credential: {field}"
                    )
            
            # 尝试建立连接以验证凭据
            conn_params = {
                "username": credentials.get("username"),
                "password": credentials.get("password"),
                "instance": credentials.get("instance"),
                "service": credentials.get("service", "api.clickzetta.com"),
                "workspace": credentials.get("workspace", "default"),
                "vcluster": credentials.get("vcluster", "default_ap"),
                "schema": credentials.get("schema", "public"),
            }
            
            # 创建连接并执行简单查询
            connection = clickzetta.connect(**conn_params)
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            connection.close()
            
        except clickzetta.Error as e:
            raise ToolProviderCredentialValidationError(
                f"Failed to connect to Lakehouse: {str(e)}"
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))