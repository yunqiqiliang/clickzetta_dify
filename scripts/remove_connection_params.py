#!/usr/bin/env python3
"""
Remove connection parameters from all tool YAML files
"""
import re
import os

# Files to process
files = [
    "tools/lakehouse_sql_query.yaml",
    "tools/vector_collection_create.yaml",
    "tools/vector_collection_list.yaml",
    "tools/vector_delete.yaml",
    "tools/vector_insert.yaml",
    "tools/vector_search.yaml"
]

# Parameters to remove
params_to_remove = ["username", "password", "instance", "service", "workspace", "vcluster", "schema"]

def remove_parameter_block(content, param_name):
    """Remove a parameter block from YAML content"""
    # Pattern to match a parameter block starting with '- name: param_name'
    # and ending before the next '- name:' or 'extra:' or end of file
    pattern = r'^- name: ' + param_name + r'\n(?:  [^\n]*\n)*'
    
    # Find and remove all matches
    content = re.sub(pattern, '', content, flags=re.MULTILINE)
    
    return content

def process_file(file_path):
    """Process a single YAML file"""
    print(f"\nProcessing {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remove each parameter
        for param in params_to_remove:
            content = remove_parameter_block(content, param)
        
        if content != original_content:
            # Write back the modified content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ Removed connection parameters from {file_path}")
        else:
            print(f"  ℹ No changes made to {file_path}")
            
    except Exception as e:
        print(f"  ✗ Error processing {file_path}: {e}")

def main():
    for file_path in files:
        if os.path.exists(file_path):
            process_file(file_path)
        else:
            print(f"  ✗ File not found: {file_path}")

if __name__ == "__main__":
    main()
    print("\nDone!")