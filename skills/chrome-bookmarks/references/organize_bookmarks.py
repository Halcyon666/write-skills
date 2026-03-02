#!/usr/bin/env python3
"""
Chrome Bookmarks Organizer
Generates an organized, categorized bookmarks HTML file from Chrome's bookmarks file.
"""

import json
import os
from collections import defaultdict
from urllib.parse import urlparse


def get_chrome_bookmarks_path():
    """Get Chrome bookmarks file path based on OS."""
    if os.name == 'nt':  # Windows
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        return os.path.join(local_app_data, 'Google', 'Chrome', 'User Data', 'Default', 'Bookmarks')
    elif os.name == 'posix':
        if os.uname().sysname == 'Darwin':  # Mac
            return os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Bookmarks')
        else:  # Linux
            return os.path.expanduser('~/.config/google-chrome/Default/Bookmarks')
    return None


def extract_all_urls(folder):
    """Recursively extract all URL bookmarks from folder."""
    urls = []
    if isinstance(folder, dict):
        if folder.get('type') == 'url':
            urls.append({
                'name': folder.get('name', ''),
                'url': folder.get('url', ''),
                'date_added': folder.get('date_added', '0'),
                'date_last_used': folder.get('date_last_used', '0'),
            })
        elif folder.get('type') == 'folder' and 'children' in folder:
            for child in folder['children']:
                urls.extend(extract_all_urls(child))
    return urls


def get_domain(url):
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower().replace('www.', '')
    except:
        return 'unknown'


def get_category(domain, name, url):
    """Categorize bookmark based on domain and name."""
    d = domain.lower()
    n = name.lower()
    u = url.lower()
    
    # AI (LLM + Image Generation)
    ai_keywords = ['openai', 'anthropic', 'gemini', 'deepseek', 'claude', 'chatgpt', 'grok', 
                  'siliconflow', 'zhipu', 'bigmodel', 'tushare', 'modelscope', 'gpugeek',
                  'colab', 'colaboratory', 'huggingface', 'langgpt', 'dify', 'llm',
                  'midjourney', 'stable-diffusion', 'dalle', 'leonardo', 'civitai', 'playground', 
                  'nightcafe', 'stability', 'replicate', 'pollinations', 'limewire', 'wombo', 
                  'demandsage', 'prompthero', 'paper2gal', 'dream.ai']
    if any(x in d for x in ai_keywords) or any(x in n for x in ['ai', 'gpt', 'llm', 'colab', 'gemini']):
        return '1-AI'
    
    # Development
    dev_keywords = ['github', 'gitlab', 'gitee', 'stackoverflow', 'geeksforgeeks', 'codecov',
                    'spring', 'maven', 'gradle', 'lombok', 'axon', 'drools', 'cola',
                    'pypi', 'python', 'django', 'flask', 'fastapi', 'scipy', 'pyvideo',
                    'mysql', 'postgres', 'mongo', 'redis', 'kafka', 'elasticsearch', 'flink', 
                    'dbeaver', 'zilliz', 'neo4j', 'milvus', 'docker', 'open-vsx', 'vercel', 'netlify']
    if any(x in d for x in dev_keywords) or any(x in n for x in ['java', 'spring', 'maven', 'python', 'database', 'sql', 'flink', 'kafka', 'cdc', 'dbeaver', 'ddd', 'github']):
        return '2-Development'
    
    # Frontend + Design
    frontend = ['vuejs', 'reactjs', 'angular', 'tailwindcss', 'webpack', 'vite', 'babel', 
                'sass', 'scss', 'less', 'css', 'flexbox', 'grid', 'pinia', 'uniapp',
                'font', 'icon', 'emoji', 'heroicons', 'keegan', 'coolors', 'symbl', 'getemoji', 
                'emojipedia', 'figma', 'canva', 'excalidraw']
    if any(x in d for x in frontend) or any(x in n for x in ['vue', 'react', 'css', 'flex', 'grid', 'tailwind', 'scss', 'uniapp', 'icon', 'emoji', 'font', 'color', 'design', 'excalidraw']):
        return '3-Frontend-Design'
    
    # Cloud + Network
    cloud = ['aliyun', 'tencentcloud', 'huawei', 'aws', 'azure', 'firebase', 'cloudflare',
             'namesilo', 'godaddy', 'adsense', 'analytics', 'search console', 'speedtest', 
             'cpolar', 'algolia']
    if any(x in d for x in cloud) or any(x in n for x in ['cloud', 'devops', 'firebase', 'cloudflare', 'domain', 'dns', 'adsense', 'analytics', 'speedtest', 'tunnel']):
        return '4-Cloud-Network'
    
    # Tech News + Blog
    news = ['infoworld', 'techcrunch', 'medium', 'zhihu', '36kr', 'juejin', 'cnblogs', 
            'csdn', 'blog.51cto', 'levelup.gitconnected', 'oracle.com/javamagazine']
    if any(x in d for x in news) or 'blog' in d:
        return '5-Tech-News'
    
    # Tools
    tools = ['notion', 'excalidraw', 'oxford', 'shanbay', 'wubi', 'xuelai', 'umi-ocr',
             'feishu', 'slack', 'dingtalk', 'wechat', 'mp.weixin', 'whatsapp', 'telegram',
             'emkei', 'meiguodizhi', 'sms-activate']
    if any(x in d for x in tools) or any(x in n for x in ['notion', 'keyboard', 'shortcut', 'ocr', 'dictionary', 'wubi', 'feishu', 'wechat', 'whatsapp', 'telegram']):
        return '6-Tools'
    
    # Media
    media = ['youtube', 'bilibili', 'vimeo', 'twitch', 'vidhub', 'alist', 'onedrive', 
             'sm.ms', 'castbox', 'podcast', 'mastersatori']
    if any(x in d for x in media) or any(x in n for x in ['video', 'media', 'podcast', 'image', 'picture']):
        return '7-Media'
    
    # Software Download
    software = ['ghxi', 'aijihuo', 'it610', 'peopleapp']
    if any(x in d for x in software) or any(x in n for x in ['download', 'crack', 'activation', 'windows', 'beyond compare', 'pycharm', 'idea']):
        return '8-Software'
    
    # Personal
    personal = ['icloud', 'halcyon', 'taobao', 'jd.com', 'tmall', 'amazon', 'goofish', 'kingfast']
    if any(x in d for x in personal) or any(x in n for x in ['shop', 'buy', 'store']):
        return '9-Personal'
    
    # Local/Temp
    if 'localhost' in u or '127.0.0.1' in u or '192.168' in u or 'router' in n or 'gov.cn' in d or 'game' in d:
        return '10-Local-Temp'
    
    return '11-Other'


def generate_html(bookmarks, show_count=False):
    """Generate Chrome bookmarks HTML."""
    categories = defaultdict(list)
    
    for bm in bookmarks:
        cat = get_category(get_domain(bm['url']), bm['name'], bm['url'])
        categories[cat].append(bm)
    
    sorted_cats = sorted(categories.keys())
    
    html = []
    html.append('<!DOCTYPE NETSCAPE-Bookmark-file-1>')
    html.append('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">')
    html.append('<TITLE>Bookmarks</TITLE>')
    html.append('<H1>Bookmarks</H1>')
    html.append('<DL><p>')
    
    for cat in sorted_cats:
        items = categories[cat]
        
        # Remove duplicates
        seen = set()
        unique = []
        for item in items:
            if item['url'] not in seen:
                seen.add(item['url'])
                unique.append(item)
        
        cat_display = cat.split('-', 1)[1] if '-' in cat else cat
        if show_count:
            cat_display = f"{cat_display} ({len(unique)})"
        
        html.append(f'    <DT><H3>{cat_display}</H3>')
        html.append('    <DL><p>')
        
        for item in sorted(unique, key=lambda x: x['name']):
            html.append(f'        <DT><A HREF="{item["url"]}" ADD_DATE="{item["date_added"]}">{item["name"]}</A>')
        
        html.append('    </DL><p>')
    
    html.append('</DL><p>')
    return '\n'.join(html)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Organize Chrome bookmarks')
    parser.add_argument('--input', '-i', help='Input bookmarks file path')
    parser.add_argument('--output', '-o', help='Output HTML file path')
    parser.add_argument('--show-count', '-c', action='store_true', help='Show bookmark count in folder names')
    args = parser.parse_args()
    
    # Default paths
    input_path = args.input or get_chrome_bookmarks_path()
    output_path = args.output or os.path.join(os.path.expanduser('~/Desktop'), 'bookmarks_organized.html')
    
    if not input_path or not os.path.exists(input_path):
        print(f"Error: Chrome bookmarks file not found at: {input_path}")
        print("Please provide the path manually with --input")
        return
    
    # Read bookmarks
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract all bookmarks
    all_bookmarks = []
    for root_name, root_data in data.get('roots', {}).items():
        all_bookmarks.extend(extract_all_urls(root_data))
    
    print(f"Total bookmarks: {len(all_bookmarks)}")
    
    # Generate HTML
    html = generate_html(all_bookmarks, show_count=args.show_count)
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\nGenerated: {output_path}")
    print("\nHow to import:")
    print("1. Chrome: Ctrl+Shift+O")
    print("2. Menu -> Import/Export")
    print("3. Import bookmarks")
    
    # Stats
    cats = defaultdict(int)
    for bm in all_bookmarks:
        cats[get_category(get_domain(bm['url']), bm['name'], bm['url'])] += 1
    
    print("\nCategory Stats:")
    for cat, cnt in sorted(cats.items()):
        cat_display = cat.split('-', 1)[1] if '-' in cat else cat
        print(f"  {cat_display}: {cnt}")


if __name__ == '__main__':
    main()
