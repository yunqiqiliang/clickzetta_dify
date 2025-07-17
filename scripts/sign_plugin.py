#!/usr/bin/env python3
"""
为 Dify 插件生成签名

注意：这是一个临时解决方案。Dify 官方可能会提供更正式的签名工具。
"""
import os
import sys
import json
import zipfile
import tempfile
import subprocess
import hashlib
import base64
from pathlib import Path
from datetime import datetime

class PluginSigner:
    def __init__(self, key_name="plugin_key"):
        self.key_name = key_name
        self.private_key_path = f"{key_name}.private.pem"
        self.public_key_path = f"{key_name}.public.pem"
    
    def generate_key_pair(self):
        """生成 RSA 密钥对"""
        if os.path.exists(self.private_key_path) and os.path.exists(self.public_key_path):
            print(f"密钥对已存在: {self.private_key_path}, {self.public_key_path}")
            return
        
        print("生成新的 RSA 密钥对...")
        
        # 生成私钥
        subprocess.run([
            "openssl", "genrsa", "-out", self.private_key_path, "4096"
        ], check=True)
        
        # 生成公钥
        subprocess.run([
            "openssl", "rsa", "-in", self.private_key_path, "-outform", "PEM", 
            "-pubout", "-out", self.public_key_path
        ], check=True)
        
        print(f"✅ 生成密钥对: {self.private_key_path}, {self.public_key_path}")
    
    def sign_plugin(self, plugin_path):
        """签名插件包"""
        if not os.path.exists(plugin_path):
            print(f"❌ 插件文件不存在: {plugin_path}")
            return None
        
        if not os.path.exists(self.private_key_path):
            print(f"❌ 私钥不存在: {self.private_key_path}")
            print("请先运行 generate_key_pair() 生成密钥对")
            return None
        
        print(f"正在签名插件: {plugin_path}")
        
        # 读取插件文件
        with open(plugin_path, 'rb') as f:
            plugin_data = f.read()
        
        # 计算 SHA256 哈希
        hash_obj = hashlib.sha256(plugin_data)
        digest = hash_obj.hexdigest()
        print(f"插件 SHA256: {digest}")
        
        # 创建签名
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(digest)
            temp_path = temp_file.name
        
        signature_path = tempfile.mktemp()
        
        try:
            # 使用私钥签名
            subprocess.run([
                "openssl", "dgst", "-sha256", "-sign", self.private_key_path,
                "-out", signature_path, temp_path
            ], check=True)
            
            # 读取签名
            with open(signature_path, 'rb') as f:
                signature = f.read()
            
            # Base64 编码签名
            signature_b64 = base64.b64encode(signature).decode('utf-8')
            
            # 创建签名信息
            signature_info = {
                "version": "1.0",
                "algorithm": "RSA-SHA256",
                "signature": signature_b64,
                "digest": digest,
                "signed_at": datetime.utcnow().isoformat() + "Z",
                "signer": self.key_name
            }
            
            # 创建带签名的插件包
            output_path = plugin_path.replace('.difypkg', '.signed.difypkg')
            
            # 解压原始插件
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(plugin_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # 添加签名文件
                signature_file = os.path.join(temp_dir, '_signature.json')
                with open(signature_file, 'w') as f:
                    json.dump(signature_info, f, indent=2)
                
                # 重新打包
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zip_ref.write(file_path, arcname)
            
            print(f"✅ 签名插件已保存: {output_path}")
            print(f"📝 签名 (前50字符): {signature_b64[:50]}...")
            
            return output_path
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(signature_path):
                os.remove(signature_path)
    
    def verify_signature(self, plugin_path):
        """验证插件签名"""
        if not os.path.exists(plugin_path):
            print(f"❌ 插件文件不存在: {plugin_path}")
            return False
        
        if not os.path.exists(self.public_key_path):
            print(f"❌ 公钥不存在: {self.public_key_path}")
            return False
        
        print(f"正在验证插件签名: {plugin_path}")
        
        try:
            # 解压插件获取签名信息
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(plugin_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                signature_file = os.path.join(temp_dir, '_signature.json')
                if not os.path.exists(signature_file):
                    print("❌ 插件未签名")
                    return False
                
                # 读取签名信息
                with open(signature_file, 'r') as f:
                    signature_info = json.load(f)
                
                # 移除签名文件后重新计算哈希
                os.remove(signature_file)
                
                # 重新打包（不含签名）以计算哈希
                temp_plugin = tempfile.mktemp(suffix='.difypkg')
                with zipfile.ZipFile(temp_plugin, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zip_ref.write(file_path, arcname)
                
                # 计算哈希
                with open(temp_plugin, 'rb') as f:
                    plugin_data = f.read()
                
                hash_obj = hashlib.sha256(plugin_data)
                digest = hash_obj.hexdigest()
                
                # 验证哈希
                if digest != signature_info.get('digest'):
                    print(f"❌ 哈希不匹配")
                    print(f"  期望: {signature_info.get('digest')}")
                    print(f"  实际: {digest}")
                    return False
                
                # 验证签名
                signature_b64 = signature_info.get('signature')
                signature = base64.b64decode(signature_b64)
                
                # 保存签名和哈希到临时文件
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                    temp_file.write(digest)
                    digest_path = temp_file.name
                
                with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
                    temp_file.write(signature)
                    sig_path = temp_file.name
                
                # 使用公钥验证
                result = subprocess.run([
                    "openssl", "dgst", "-sha256", "-verify", self.public_key_path,
                    "-signature", sig_path, digest_path
                ], capture_output=True, text=True)
                
                # 清理临时文件
                os.remove(digest_path)
                os.remove(sig_path)
                os.remove(temp_plugin)
                
                if result.returncode == 0:
                    print("✅ 签名验证成功")
                    print(f"📅 签名时间: {signature_info.get('signed_at')}")
                    print(f"🔑 签名者: {signature_info.get('signer')}")
                    return True
                else:
                    print("❌ 签名验证失败")
                    print(result.stderr)
                    return False
                    
        except Exception as e:
            print(f"❌ 验证过程出错: {e}")
            return False

def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  生成密钥对: python sign_plugin.py generate")
        print("  签名插件:   python sign_plugin.py sign <plugin.difypkg>")
        print("  验证签名:   python sign_plugin.py verify <plugin.signed.difypkg>")
        print("  显示公钥:   python sign_plugin.py show-public-key")
        sys.exit(1)
    
    command = sys.argv[1]
    signer = PluginSigner("clickzetta_plugin")
    
    if command == "generate":
        signer.generate_key_pair()
    
    elif command == "sign":
        if len(sys.argv) < 3:
            print("请指定要签名的插件文件")
            sys.exit(1)
        plugin_file = sys.argv[2]
        signer.sign_plugin(plugin_file)
    
    elif command == "verify":
        if len(sys.argv) < 3:
            print("请指定要验证的插件文件")
            sys.exit(1)
        plugin_file = sys.argv[2]
        success = signer.verify_signature(plugin_file)
        sys.exit(0 if success else 1)
    
    elif command == "show-public-key":
        if os.path.exists(signer.public_key_path):
            with open(signer.public_key_path, 'r') as f:
                print(f.read())
        else:
            print(f"公钥文件不存在: {signer.public_key_path}")
            print("请先运行 'python sign_plugin.py generate' 生成密钥对")
    
    else:
        print(f"未知命令: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()