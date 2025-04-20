# 网页爬虫工具

这是一个用于爬取网页内容的 Python 工具。它可以提取网页中的标题、文本内容、视频链接和封面图片等信息。

## 功能特点

- 支持 HTTPS 网页爬取
- 自动提取页面标题
- 提取文本内容
- 识别视频链接（支持 YouTube）
- 获取封面图片
- 返回 JSON 格式数据
- 包含错误处理机制

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

```python
from scraper import scrape_transcript

url = "你的目标网页URL"
result = scrape_transcript(url)
print(result)
```

## 返回数据格式

```json
{
    "title": "页面标题",
    "transcript": "文本内容",
    "video_link": "视频链接",
    "cover_image": "封面图片链接",
    "timestamp": "爬取时间"
}
```

## 注意事项

1. 确保目标网站允许爬虫访问
2. 建议设置适当的请求间隔
3. 遵守网站的robots.txt规则
4. 处理好异常情况 