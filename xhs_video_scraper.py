import requests
import json
import re
from fake_useragent import UserAgent
import time
import random
import logging
import urllib.parse

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XHSVideoScraper:
    def __init__(self):
        """初始化爬虫类"""
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Cookie': '',  # 需要填入你的小红书Cookie
            'Referer': 'https://www.xiaohongshu.com',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Origin': 'https://www.xiaohongshu.com',
            'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-S': '',  # 这个值需要从浏览器中获取
            'X-T': str(int(time.time())),
        }
        self.session.headers.update(self.headers)

    def get_note_id(self, url):
        """从URL中提取笔记ID"""
        patterns = [
            r'/explore/([a-zA-Z0-9]+)',
            r'/discovery/item/([a-zA-Z0-9]+)',
            r'xhslink.com/([a-zA-Z0-9]+)',
            r'/items/([a-zA-Z0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_video_info(self, note_id):
        """获取视频信息"""
        try:
            # 构建API URL
            api_url = f'https://www.xiaohongshu.com/api/sns/web/v1/feed?noteIds=["{note_id}"]'
            logger.info(f"正在请求: {api_url}")
            
            # 添加随机延迟
            time.sleep(random.uniform(2, 4))
            
            # 获取页面HTML
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            
            # 保存响应内容用于调试
            with open('response.json', 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.info("已保存响应内容到response.json")
            
            try:
                data = response.json()
                if data.get('code') != 0:
                    logger.error(f"API返回错误: {data.get('msg')}")
                    return {"error": f"API返回错误: {data.get('msg')}"}
                
                notes = data.get('data', {}).get('notes', [])
                if not notes:
                    logger.error("未找到笔记数据")
                    return {"error": "未找到笔记数据"}
                
                note = notes[0]
                if 'video' not in note:
                    logger.error("该笔记不包含视频")
                    return {"error": "该笔记不包含视频"}
                
                video_info = {
                    'video_url': note['video'].get('url'),
                    'cover_url': note['video'].get('cover', {}).get('url'),
                    'duration': note['video'].get('duration'),
                    'title': note.get('title', ''),
                    'description': note.get('desc', ''),
                    'user': note.get('user', {}).get('nickname', '')
                }
                
                if not video_info['video_url']:
                    logger.error("未找到视频URL")
                    return {"error": "未找到视频URL"}
                
                logger.info("成功获取视频信息")
                return video_info
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {str(e)}")
                return {"error": f"JSON解析错误: {str(e)}"}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求错误: {str(e)}")
            return {"error": f"请求错误: {str(e)}"}
        except Exception as e:
            logger.error(f"未知错误: {str(e)}")
            return {"error": f"未知错误: {str(e)}"}

    def download_video(self, video_url, output_path):
        """下载视频"""
        try:
            if not video_url:
                return False, "视频URL为空"
            
            logger.info(f"开始下载视频: {video_url}")
            
            # 添加随机延迟
            time.sleep(random.uniform(2, 4))
            
            # 更新请求头
            download_headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Encoding': 'identity;q=1, *;q=0',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Range': 'bytes=0-',
                'Referer': 'https://www.xiaohongshu.com/',
                'Origin': 'https://www.xiaohongshu.com',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
            }
            
            response = requests.get(video_url, headers=download_headers, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1KB
            downloaded_size = 0
            
            with open(output_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    f.write(data)
                    downloaded_size += len(data)
                    if total_size:
                        progress = (downloaded_size / total_size) * 100
                        logger.info(f"下载进度: {progress:.2f}%")
                    
            logger.info("视频下载完成")
            return True, "下载成功"
            
        except Exception as e:
            logger.error(f"下载失败: {str(e)}")
            return False, f"下载失败: {str(e)}"

def main():
    """主函数"""
    scraper = XHSVideoScraper()
    
    # 获取用户输入
    url = input("请输入小红书视频链接：")
    note_id = scraper.get_note_id(url)
    
    if not note_id:
        logger.error("无效的小红书链接")
        return
        
    # 获取视频信息
    logger.info("\n正在获取视频信息...")
    video_info = scraper.get_video_info(note_id)
    
    if "error" in video_info:
        logger.error(f"错误: {video_info['error']}")
        return
        
    # 打印视频信息
    logger.info("\n视频信息:")
    print(json.dumps(video_info, ensure_ascii=False, indent=2))
    
    # 下载视频
    if video_info.get('video_url'):
        logger.info("\n开始下载视频...")
        output_path = f"xhs_video_{note_id}.mp4"
        success, message = scraper.download_video(video_info['video_url'], output_path)
        logger.info(message)
        if success:
            logger.info(f"视频已保存至: {output_path}")

if __name__ == "__main__":
    main() 