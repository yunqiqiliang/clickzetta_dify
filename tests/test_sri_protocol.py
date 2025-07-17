#!/usr/bin/env python3
"""按照 Dify SRI (Server Runtime Interface) 协议测试插件"""

import os
import sys
import json
import uuid
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# 加载环境变量
load_dotenv()

class DifyPluginTester:
    """Dify 插件测试器"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent.parent
        self.process = None
        self.session_id = str(uuid.uuid4())
        self.user_id = "test-user"
        
    def start_plugin(self):
        """启动插件进程"""
        print("启动插件进程...")
        env = os.environ.copy()
        env['INSTALL_METHOD'] = 'local'
        
        self.process = subprocess.Popen(
            [sys.executable, str(self.project_dir / "main.py")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,
            env=env
        )
        
        # 读取插件配置
        config_line = self.process.stdout.readline()
        if config_line:
            try:
                config = json.loads(config_line.strip())
                print(f"插件配置: {json.dumps(config, indent=2, ensure_ascii=False)}")
                return True
            except json.JSONDecodeError:
                print(f"无法解析配置: {config_line}")
                return False
        return False
    
    def send_request(self, request: Dict[str, Any]):
        """发送请求到插件"""
        request_str = json.dumps(request)
        print(f"\n发送请求: {request_str}")
        self.process.stdin.write(request_str + "\n")
        self.process.stdin.flush()
    
    def read_response(self):
        """读取插件响应"""
        responses = []
        while True:
            line = self.process.stdout.readline()
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
                
            try:
                response = json.loads(line)
                print(f"收到响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
                responses.append(response)
                
                # 检查是否是结束响应
                if response.get("type") == "invoke:response" and \
                   response.get("response", {}).get("event") == "done":
                    break
                    
            except json.JSONDecodeError:
                print(f"无法解析响应: {line}")
        
        return responses
    
    def invoke_tool(self, tool_name: str, tool_params: Dict[str, Any]):
        """调用工具"""
        request_id = str(uuid.uuid4())
        
        # 构建请求
        request = {
            "type": "invoke:request",
            "request": {
                "request_id": request_id,
                "session_id": self.session_id,
                "user_id": self.user_id,
                "app_id": "test-app",
                "tenant_id": "test-tenant",
                "type": "tool",
                "invoke_type": PluginInvokeType.Tool,
                "action": "invoke",
                "data": {
                    "tool": tool_name,
                    "parameters": tool_params
                }
            }
        }
        
        self.send_request(request)
        return self.read_response()
    
    def close(self):
        """关闭插件进程"""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            print("\n插件进程已关闭")

def test_lakehouse_tools():
    """测试 Lakehouse 工具"""
    tester = DifyPluginTester()
    
    try:
        # 启动插件
        if not tester.start_plugin():
            print("插件启动失败")
            return
        
        # 等待插件初始化
        time.sleep(1)
        
        # 准备连接参数
        connection_params = {
            "username": os.getenv("LAKEHOUSE_USERNAME"),
            "password": os.getenv("LAKEHOUSE_PASSWORD"),
            "instance": os.getenv("LAKEHOUSE_INSTANCE"),
            "service": os.getenv("LAKEHOUSE_SERVICE"),
            "workspace": os.getenv("LAKEHOUSE_WORKSPACE"),
            "vcluster": os.getenv("LAKEHOUSE_VCLUSTER"),
            "schema": os.getenv("LAKEHOUSE_SCHEMA"),
        }
        
        print("\n=== 测试 1: SQL 查询 - 显示表 ===")
        response = tester.invoke_tool("lakehouse_sql_query", {
            **connection_params,
            "query": "SHOW TABLES",
            "max_rows": 10
        })
        
        print("\n=== 测试 2: 创建测试表 ===")
        response = tester.invoke_tool("lakehouse_sql_query", {
            **connection_params,
            "query": """
            CREATE TABLE IF NOT EXISTS sri_test (
                id STRING,
                name STRING,
                value DOUBLE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            "max_rows": 10
        })
        
        print("\n=== 测试 3: 插入数据 ===")
        response = tester.invoke_tool("lakehouse_sql_query", {
            **connection_params,
            "query": """
            INSERT INTO sri_test (id, name, value) VALUES 
            ('1', 'Test Item 1', 10.5),
            ('2', 'Test Item 2', 20.3)
            """,
            "max_rows": 10
        })
        
        print("\n=== 测试 4: 查询数据 ===")
        response = tester.invoke_tool("lakehouse_sql_query", {
            **connection_params,
            "query": "SELECT * FROM sri_test ORDER BY id",
            "max_rows": 10
        })
        
        print("\n=== 测试 5: 列出向量集合 ===")
        response = tester.invoke_tool("vector_collection_list", connection_params)
        
        print("\n测试完成!")
        
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        tester.close()

# 定义 PluginInvokeType 常量
class PluginInvokeType:
    Tool = "tool"
    Model = "model"
    Endpoint = "endpoint"

if __name__ == "__main__":
    test_lakehouse_tools()