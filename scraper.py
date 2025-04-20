import requests
from bs4 import BeautifulSoup
import json
from urllib3.exceptions import InsecureRequestWarning
import re
import datetime

# 禁用 SSL 警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def scrape_transcript(url):
    try:
        # 发送请求时禁用 SSL 验证
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取标题
        title = soup.find('h1', class_='entry-title')
        title = title.text if title else "未找到标题"
        
        # 提取文本内容
        transcript_segments = soup.find_all('div', class_='ts-segment')
        transcript_text = '\n'.join([segment.text.strip() for segment in transcript_segments])
        
        # 提取视频链接
        video_link = soup.find('a', href=re.compile(r'youtube\.com|youtu\.be'))
        video_url = video_link['href'] if video_link else "未找到视频链接"
        
        # 提取封面图片
        cover_image = soup.find('img', class_='featured-image')
        cover_url = cover_image['src'] if cover_image else "未找到封面图片"
        
        # 构建返回数据
        result = {
            "title": title,
            "transcript": transcript_text,
            "video_link": video_url,
            "cover_image": cover_url,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        print(f"抓取失败: {str(e)}")
        return {
            "error": f"抓取失败，请检查URL是否正确或稍后重试: {str(e)}"
        }

if __name__ == "__main__":
    url = "https://lexfridman.com/robert-rodriguez-transcript/"
    result = scrape_transcript(url)
    print(json.dumps(result, ensure_ascii=False, indent=2)) 