import requests
from bs4 import BeautifulSoup
import json
import os
import time
from typing import Dict, Optional, List
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LexFridmanScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """发送HTTP请求并处理重试逻辑"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"达到最大重试次数: {str(e)}")
                    return None
                time.sleep(2 ** attempt)  # 指数退避
        return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取文章标题"""
        # 按优先级尝试不同的选择器
        selectors = [
            ('h1', {'class_': 'entry-title'}),
            ('h1', {}),
            ('title', {})
        ]
        
        for tag, attrs in selectors:
            element = soup.find(tag, **attrs)
            if element:
                title = element.text.strip()
                if title:
                    return title
        
        return "未找到标题"

    def _extract_content(self, soup: BeautifulSoup) -> List[str]:
        """提取文章内容"""
        content = []
        
        # 尝试找到主要内容区域
        main_content = soup.find('div', class_='entry-content') or soup
        
        # 按优先级尝试不同的内容选择器
        content_elements = (
            main_content.find_all('div', class_='ts-segment') or 
            main_content.find_all(['p', 'div'], class_=['paragraph', 'content']) or
            main_content.find_all(['p', 'div'])
        )

        for element in content_elements:
            text = element.text.strip()
            if text and not self._is_navigation_text(text):
                content.append(text)

        return content

    def _is_navigation_text(self, text: str) -> bool:
        """检查是否为导航文本"""
        nav_keywords = ['next post', 'previous post', 'menu', 'search', 'skip to content']
        return any(keyword in text.lower() for keyword in nav_keywords)

    def _extract_video_link(self, soup: BeautifulSoup) -> Optional[str]:
        """提取视频链接"""
        for link in soup.find_all('a'):
            href = link.get('href', '').lower()
            if 'youtube.com' in href or 'youtu.be' in href:
                return link['href']
        return None

    def _extract_cover_image(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """提取封面图片"""
        # 尝试找到主图片
        img_selectors = [
            ('img', {'class_': 'featured-image'}),
            ('img', {'class_': 'wp-post-image'}),
            ('meta', {'property': 'og:image'}),
            ('img', {})
        ]

        for tag, attrs in img_selectors:
            element = soup.find(tag, **attrs)
            if element:
                # 对于meta标签，使用content属性
                if tag == 'meta':
                    src = element.get('content')
                else:
                    src = element.get('src')
                
                if src:
                    # 处理相对URL
                    if not src.startswith(('http://', 'https://')):
                        src = f"{base_url.rstrip('/')}/{src.lstrip('/')}"
                    return src
        
        return None

    def scrape_article(self, url: str) -> Optional[Dict]:
        """抓取文章内容的主方法"""
        try:
            logger.info(f"开始抓取文章: {url}")
            
            # 发送请求
            response = self._make_request(url)
            if not response:
                return None

            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取内容
            title = self._extract_title(soup)
            content = self._extract_content(soup)
            video_link = self._extract_video_link(soup)
            base_url = '/'.join(url.split('/')[:3])  # 获取基础URL
            cover_image = self._extract_cover_image(soup, base_url)

            # 验证必要内容
            if not content:
                logger.error("未能提取到文章内容")
                return None

            # 整理数据
            article_data = {
                'title': title,
                'content': '\n'.join(content),
                'video_link': video_link,
                'cover_image': cover_image
            }

            # 保存数据
            self._save_to_json(article_data)
            
            logger.info("文章抓取成功")
            return article_data

        except Exception as e:
            logger.error(f"抓取过程中出现错误: {str(e)}", exc_info=True)
            return None

    def _save_to_json(self, data: Dict) -> None:
        """保存数据到JSON文件"""
        try:
            if not os.path.exists('output'):
                os.makedirs('output')
            
            output_file = 'output/article_data.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"数据已保存到: {output_file}")
            
        except Exception as e:
            logger.error(f"保存JSON文件时出错: {str(e)}")

def main():
    scraper = LexFridmanScraper()
    url = 'https://lexfridman.com/robert-rodriguez-transcript'
    
    logger.info("开始抓取文章...")
    result = scraper.scrape_article(url)
    
    if result:
        logger.info("抓取成功!")
        logger.info(f"标题: {result['title']}")
        logger.info(f"视频链接: {result['video_link']}")
        logger.info(f"封面图片: {result['cover_image']}")
    else:
        logger.error("抓取失败!")

if __name__ == "__main__":
    main() 