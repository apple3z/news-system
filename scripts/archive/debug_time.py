#!/usr/bin/env python3
"""调试时间解析"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def get_page(url):
    """获取页面内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = resp.apparent_encoding or 'utf-8'
        return resp.text
    except Exception as e:
        print(f"请求失败: {e}")
        return ""

def parse_time_debug(soup, url):
    """从新闻页面解析发布时间 - 调试版本"""
    time_str = ''
    print(f"\n解析URL: {url}")
    print("="*80)
    
    # 1. 从 meta 标签获取
    print("\n1. 检查 meta 标签:")
    for meta in soup.find_all('meta'):
        prop = meta.get('property', '').lower()
        name = meta.get('name', '').lower()
        content = meta.get('content', '')
        if 'time' in prop or 'time' in name or 'date' in prop or 'date' in name:
            print(f"   - {prop or name} = {content[:100]}")
            if content and len(content) > 5:
                time_str = content
                break
    
    # 2. 从常见的时间标签获取
    print("\n2. 检查常见时间标签:")
    time_selectors = [
        'time', '.time', '.date', '.pub-time', '.publish-time', 
        '.article-time', '.post-time', '.meta-time', '.date-time'
    ]
    for sel in time_selectors:
        elem = soup.select_one(sel)
        if elem:
            text = elem.get_text(strip=True)
            print(f"   - {sel} = {text}")
            if text and len(text) > 5:
                time_str = text
                break
    
    # 3. 根据不同网站的特定选择器
    print("\n3. 检查网站特定选择器:")
    if '163.com' in url:
        elem = soup.select_one('.post_time_source, .time, .pub_time')
        if elem:
            time_str = elem.get_text(strip=True)
            print(f"   - 网易选择器: {time_str}")
    elif 'sina.com.cn' in url:
        elem = soup.select_one('.date, .time, .pub_date')
        if elem:
            time_str = elem.get_text(strip=True)
            print(f"   - 新浪选择器: {time_str}")
    elif 'ifeng.com' in url:
        elem = soup.select_one('.time, .pubTime')
        if elem:
            time_str = elem.get_text(strip=True)
            print(f"   - 凤凰选择器: {time_str}")
    
    # 4. 正则解析时间字符串
    print(f"\n4. 最终提取的 time_str: '{time_str}'")
    if time_str:
        date_patterns = [
            r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})[日]?',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, time_str)
            if match:
                year, month, day = match.groups()
                result = f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
                print(f"   - 匹配成功: {result}")
                return result
    
    # 如果无法解析，返回当前日期
    fallback = datetime.now().strftime("%Y-%m-%d")
    print(f"5. 使用 fallback: {fallback}")
    return fallback

# 测试一下第一条新闻
test_url = "https://tech.163.com/"
print(f"测试首页: {test_url}")
html = get_page(test_url)
if html:
    soup = BeautifulSoup(html, 'html.parser')
    # 找一条新闻链接
    for a in soup.find_all('a', href=True):
        title = a.get_text(strip=True)
        link = a.get('href', '')
        if title and len(title) > 10 and any(kw in title for kw in ['AI', '智能', '大模型']):
            if link.startswith('/'):
                link = "https://tech.163.com" + link
            print(f"\n找到新闻: {title}")
            print(f"链接: {link}")
            
            # 获取详情页
            detail_html = get_page(link)
            if detail_html:
                detail_soup = BeautifulSoup(detail_html, 'html.parser')
                parsed_time = parse_time_debug(detail_soup, link)
                print(f"\n最终解析时间: {parsed_time}")
            break
