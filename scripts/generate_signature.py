#!/usr/bin/env python3
"""
Generate signature for Dify plugin
"""
import os
import subprocess
import hashlib
import base64
from pathlib import Path

def generate_key_pair(key_name="clickzetta"):
    """生成 RSA 密钥对"""
    private_key = f"{key_name}.private.pem"
    public_key = f"{key_name}.public.pem"
    
    # 生成私钥
    subprocess.run([
        "openssl", "genrsa", "-out", private_key, "2048"
    ], check=True)
    
    # 生成公钥
    subprocess.run([
        "openssl", "rsa", "-in", private_key, "-outform", "PEM", 
        "-pubout", "-out", public_key
    ], check=True)
    
    print(f"Generated key pair: {private_key}, {public_key}")
    return private_key, public_key

def sign_plugin(plugin_path, private_key_path):
    """签名插件包"""
    # 读取插件文件
    with open(plugin_path, 'rb') as f:
        plugin_data = f.read()
    
    # 计算 SHA256 哈希
    hash_obj = hashlib.sha256(plugin_data)
    digest = hash_obj.digest()
    
    # 创建临时文件存储哈希
    with open('temp_hash.bin', 'wb') as f:
        f.write(digest)
    
    # 使用私钥签名哈希
    signature_file = 'temp_signature.bin'
    subprocess.run([
        "openssl", "dgst", "-sha256", "-sign", private_key_path,
        "-out", signature_file, "temp_hash.bin"
    ], check=True)
    
    # 读取签名
    with open(signature_file, 'rb') as f:
        signature = f.read()
    
    # Base64 编码签名
    signature_b64 = base64.b64encode(signature).decode('utf-8')
    
    # 创建签名文件
    signed_plugin_path = plugin_path.replace('.difypkg', '.signed.difypkg')
    
    # 简单方案：将签名附加到文件末尾
    # 实际的 Dify 可能使用不同的格式
    with open(signed_plugin_path, 'wb') as f:
        f.write(plugin_data)
        f.write(b'\n---DIFY_SIGNATURE---\n')
        f.write(signature_b64.encode('utf-8'))
    
    # 清理临时文件
    os.remove('temp_hash.bin')
    os.remove('temp_signature.bin')
    
    print(f"Signed plugin saved as: {signed_plugin_path}")
    print(f"Signature (Base64): {signature_b64[:50]}...")
    
    return signed_plugin_path

if __name__ == "__main__":
    # 生成密钥对
    private_key, public_key = generate_key_pair("clickzetta")
    
    # 签名插件
    plugin_file = "clickzetta_lakehouse.difypkg"
    if os.path.exists(plugin_file):
        signed_plugin = sign_plugin(plugin_file, private_key)
        print("\nPlugin signed successfully!")
        print(f"Private key: {private_key}")
        print(f"Public key: {public_key}")
        print(f"Signed plugin: {signed_plugin}")
    else:
        print(f"Plugin file {plugin_file} not found!")