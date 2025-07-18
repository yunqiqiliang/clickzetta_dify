import os
import logging
from typing import Optional, Dict, Any
import clickzetta

logger = logging.getLogger(__name__)

class LakehouseConnection:
    """管理 Clickzetta Lakehouse 连接的单例类"""
    
    _instance = None
    _connection: Optional[Any] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_connection(self, config: Dict[str, Any]) -> Any:
        """获取或创建 Lakehouse 连接"""
        if self._connection is None or not self._is_connection_alive():
            self._connection = self._create_connection(config)
        return self._connection
    
    def _create_connection(self, config: Dict[str, Any]) -> Any:
        """创建新的 Lakehouse 连接"""
        try:
            # 从配置或环境变量获取连接参数
            conn_params = {
                "username": config.get("username") or os.getenv("LAKEHOUSE_USERNAME"),
                "password": config.get("password") or os.getenv("LAKEHOUSE_PASSWORD"),
                "instance": config.get("instance") or os.getenv("LAKEHOUSE_INSTANCE"),
                "service": config.get("service", "api.clickzetta.com"),
                "workspace": config.get("workspace", "quick_start"),
                "vcluster": config.get("vcluster", "default_ap"),
                "schema": config.get("schema", "dify"),
            }
            
            # 验证必需参数
            required_params = ["username", "password", "instance"]
            for param in required_params:
                if not conn_params.get(param):
                    raise ValueError(f"Missing required parameter: {param}")
            
            logger.info(f"Connecting to Lakehouse instance: {conn_params['instance']}")
            connection = clickzetta.connect(**conn_params)
            
            # 测试连接
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            logger.info("Successfully connected to Lakehouse")
            return connection
            
        except Exception as e:
            logger.error(f"Failed to connect to Lakehouse: {str(e)}")
            raise
    
    def _is_connection_alive(self) -> bool:
        """检查连接是否仍然有效"""
        if self._connection is None:
            return False
        
        try:
            with self._connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True
        except:
            return False
    
    def close(self):
        """关闭连接"""
        if self._connection:
            try:
                self._connection.close()
            except:
                pass
            self._connection = None