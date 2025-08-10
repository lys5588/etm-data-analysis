#!/usr/bin/env python3
"""
ETM API 连接诊断工具
用于排查API连接问题的详细诊断
"""

import requests
import json
import socket
import ssl
from urllib.parse import urlparse
import os

def test_basic_connectivity():
    """测试基础网络连接"""
    print("=== 基础网络连接测试 ===")
    
    # 测试DNS解析
    try:
        hostname = "engine.energytransitionmodel.com"
        ip = socket.gethostbyname(hostname)
        print(f"✓ DNS解析成功: {hostname} -> {ip}")
    except socket.gaierror as e:
        print(f"✗ DNS解析失败: {e}")
        return False
    
    # 测试端口连接
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((hostname, 443))
        sock.close()
        
        if result == 0:
            print("✓ 端口443连接成功")
        else:
            print(f"✗ 端口443连接失败，错误码: {result}")
            return False
    except Exception as e:
        print(f"✗ 端口连接测试失败: {e}")
        return False
    
    return True

def test_ssl_certificate():
    """测试SSL证书"""
    print("\n=== SSL证书测试 ===")
    
    try:
        hostname = "engine.energytransitionmodel.com"
        context = ssl.create_default_context()
        
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                print(f"✓ SSL证书有效")
                print(f"  颁发给: {cert.get('subject', [])}")
                print(f"  颁发者: {cert.get('issuer', [])}")
                print(f"  有效期至: {cert.get('notAfter', '未知')}")
                return True
    except ssl.SSLError as e:
        print(f"✗ SSL证书错误: {e}")
    except Exception as e:
        print(f"✗ SSL测试失败: {e}")
    
    return False

def test_http_endpoints():
    """测试HTTP端点响应"""
    print("\n=== HTTP端点测试 ===")
    
    base_url = "https://engine.energytransitionmodel.com/api/v3"
    endpoints = [
        "/health",
        "/scenarios",
        "/"
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            print(f"✓ {endpoint}: {response.status_code} ({len(response.content)} bytes)")
            if response.status_code == 401:
                print("  注意: 需要认证 (401 Unauthorized)")
            elif response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  响应类型: JSON, 键值: {list(data.keys())[:5]}")
                except:
                    print(f"  响应类型: 文本 ({response.text[:100]}...)")
        except requests.exceptions.Timeout:
            print(f"✗ {endpoint}: 超时")
        except requests.exceptions.ConnectionError as e:
            print(f"✗ {endpoint}: 连接错误 - {type(e).__name__}")
        except Exception as e:
            print(f"✗ {endpoint}: 其他错误 - {e}")

def test_authentication(token):
    """测试认证"""
    print("\n=== 认证测试 ===")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    url = "https://engine.energytransitionmodel.com/api/v3/scenarios"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"认证测试结果: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ 认证成功")
            try:
                data = response.json()
                print(f"  场景数量: {len(data)}")
            except:
                pass
        elif response.status_code == 401:
            print("✗ 认证失败 - 无效token")
        elif response.status_code == 403:
            print("✗ 认证失败 - 权限不足")
        else:
            print(f"✗ 认证失败 - 状态码: {response.status_code}")
            print(f"  响应: {response.text[:200]}")
            
    except Exception as e:
        print(f"✗ 认证测试失败: {e}")

def test_proxy_issues():
    """测试代理问题"""
    print("\n=== 代理检测 ===")
    
    # 检查环境变量
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    proxies = {}
    
    for var in proxy_vars:
        value = os.getenv(var)
        if value:
            print(f"检测到代理变量 {var}: {value}")
            if var.lower() in ['http_proxy', 'https_proxy']:
                proxies[var.split('_')[0].lower()] = value
    
    if proxies:
        print(f"使用代理配置: {proxies}")
        try:
            response = requests.get('https://engine.energytransitionmodel.com/api/v3/health', 
                                  proxies=proxies, timeout=10)
            print(f"通过代理连接结果: {response.status_code}")
        except Exception as e:
            print(f"代理连接失败: {e}")
    else:
        print("未检测到代理配置")

def test_token_file():
    """测试token文件"""
    print("\n=== Token文件测试 ===")
    
    token_file = "token.txt"
    if not os.path.exists(token_file):
        print(f"✗ Token文件 {token_file} 不存在")
        return None
    
    try:
        with open(token_file, 'r') as f:
            token = f.read().strip()
        
        if not token:
            print("✗ Token文件为空")
            return None
        
        print(f"✓ Token文件存在，长度: {len(token)} 字符")
        
        # 保持原始格式，不移除前缀
        if token.startswith('etm_'):
            print("  检测到etm_前缀，保持原格式")
        
        # 检查token格式
        if len(token) > 100 and '.' in token:
            print("✓ Token格式看起来有效")
            return token
        else:
            print("⚠ Token格式可能无效")
            return token
            
    except Exception as e:
        print(f"✗ 读取token文件失败: {e}")
        return None

def run_full_diagnostic():
    """运行完整诊断"""
    print("ETM API 连接诊断工具")
    print("=" * 50)
    
    # 测试基础连接
    basic_ok = test_basic_connectivity()
    if not basic_ok:
        print("\n基础网络连接失败，请检查网络设置")
        return
    
    # 测试SSL
    ssl_ok = test_ssl_certificate()
    if not ssl_ok:
        print("\nSSL证书问题，可能是网络拦截或防火墙")
        return
    
    # 测试代理
    test_proxy_issues()
    
    # 测试HTTP端点
    test_http_endpoints()
    
    # 测试token文件
    token = test_token_file()
    if token:
        test_authentication(token)
    
    print("\n" + "=" * 50)
    print("诊断完成！请根据以上结果排查问题。")
    
    # 提供建议
    print("\n常见问题排查建议:")
    print("1. 检查网络连接和防火墙设置")
    print("2. 确认token文件存在且有效")
    print("3. 尝试使用手机热点测试网络环境")
    print("4. 检查是否需要使用代理服务器")
    print("5. 确认API端点URL是否正确")

if __name__ == "__main__":
    run_full_diagnostic()