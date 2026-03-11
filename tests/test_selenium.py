#!/usr/bin/env python3
"""
前端功能测试 - 使用 Selenium
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_admin_page():
    print("=" * 60)
    print("前端功能测试")
    print("=" * 60)
    
    # 配置 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    driver = None
    try:
        print("\n1. 启动浏览器...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        print("2. 访问系统管理页面...")
        driver.get('http://localhost:5000/sys')
        time.sleep(2)
        
        # 获取页面标题
        title = driver.title
        print(f"   页面标题: {title}")
        
        # 检查 tabs 容器
        print("\n3. 检查 tabs 元素...")
        tabs = driver.find_elements(By.CLASS_NAME, 'tab')
        print(f"   找到 {len(tabs)} 个 tab 元素")
        
        for i, tab in enumerate(tabs):
            print(f"   Tab {i+1}: {tab.text} - data-tab: {tab.get_attribute('data-tab')}")
        
        # 检查 tab-content 元素
        print("\n4. 检查 tab-content 元素...")
        contents = driver.find_elements(By.CLASS_NAME, 'tab-content')
        print(f"   找到 {len(contents)} 个 tab-content 元素")
        
        for i, content in enumerate(contents):
            print(f"   Content {i+1}: id={content.get_attribute('id')}, class={content.get_attribute('class')}")
        
        # 尝试点击版本历史标签
        print("\n5. 尝试点击'版本历史'标签...")
        versions_tab = driver.find_element(By.CSS_SELECTOR, 'button[data-tab="versions"]')
        print(f"   找到版本历史按钮: {versions_tab.text}")
        versions_tab.click()
        time.sleep(1)
        
        # 检查是否切换成功
        active_tab = driver.find_element(By.CSS_SELECTOR, 'button.tab.active')
        print(f"   点击后激活的标签: {active_tab.text}")
        
        # 检查版本历史内容是否显示
        versions_content = driver.find_element(By.ID, 'tab-versions')
        is_displayed = versions_content.is_displayed()
        print(f"   版本历史内容显示: {is_displayed}")
        
        # 检查版本树是否加载
        version_tree = driver.find_elements(By.ID, 'versionTree')
        if version_tree:
            print(f"   版本树元素存在: 是")
        
        # 获取控制台日志
        print("\n6. 获取控制台日志...")
        logs = driver.get_log('browser')
        for log in logs:
            if log['level'] in ['SEVERE', 'ERROR']:
                print(f"   [{log['level']}] {log['message']}")
        
        print("\n✅ 测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    test_admin_page()
