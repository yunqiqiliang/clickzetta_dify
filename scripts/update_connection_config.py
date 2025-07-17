#!/usr/bin/env python3
"""
Update all tool files to use provider credentials
"""
import os
import glob

# The new _get_connection_config method
new_method = '''    def _get_connection_config(self, tool_parameters: dict[str, Any]) -> Dict[str, Any]:
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
        }'''

# Files to update
files = [
    "tools/vector_collection_create.py",
    "tools/vector_collection_list.py",
    "tools/vector_delete.py",
    "tools/vector_insert.py",
    "tools/vector_search.py"
]

for file_path in files:
    print(f"Updating {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the _get_connection_config method
    start_marker = "    def _get_connection_config(self, tool_parameters: dict[str, Any]) -> Dict[str, Any]:"
    end_marker = "        }"
    
    start_idx = content.find(start_marker)
    if start_idx != -1:
        # Find the end of the method
        end_idx = content.find(end_marker, start_idx)
        if end_idx != -1:
            end_idx += len(end_marker)
            
            # Replace the method
            new_content = content[:start_idx] + new_method + content[end_idx:]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✓ Updated successfully")
        else:
            print(f"  ✗ Could not find end of method")
    else:
        print(f"  ✗ Could not find _get_connection_config method")

print("\nDone!")