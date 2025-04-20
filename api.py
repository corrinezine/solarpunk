from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict
from lex_scraper import LexFridmanScraper
import uvicorn
import logging
from datetime import datetime
import traceback

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="文章内容抓取API",
    description="提供网页文章内容抓取服务的REST API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义请求模型
class ScrapeRequest(BaseModel):
    url: HttpUrl = Field(..., description="要抓取的文章URL")

# 定义响应模型
class ScrapeResponse(BaseModel):
    title: str = Field(..., description="文章标题")
    content: str = Field(..., description="文章内容")
    video_link: Optional[str] = Field(None, description="视频链接(如果有)")
    cover_image: Optional[str] = Field(None, description="封面图片URL(如果有)")
    timestamp: str = Field(..., description="抓取时间")

# 定义错误响应模型
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: str

# 创建爬虫实例
scraper = LexFridmanScraper()

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_detail = {
        "error": "服务器内部错误",
        "detail": str(exc),
        "traceback": traceback.format_exc(),
        "timestamp": datetime.now().isoformat()
    }
    logger.error(f"发生错误: {str(exc)}\n{error_detail['traceback']}")
    return JSONResponse(
        status_code=500,
        content=error_detail
    )

@app.post("/scrape", response_model=ScrapeResponse, 
          responses={
              500: {"model": ErrorResponse, "description": "抓取失败"},
              422: {"model": ErrorResponse, "description": "无效的请求参数"}
          })
async def scrape_article(request: ScrapeRequest):
    """
    抓取指定URL的文章内容
    
    参数:
    - url: 要抓取的文章URL
    
    返回:
    - title: 文章标题
    - content: 文章内容
    - video_link: 视频链接(如果有)
    - cover_image: 封面图片URL(如果有)
    - timestamp: 抓取时间
    """
    try:
        logger.info(f"收到抓取请求: {request.url}")
        
        # 调用爬虫进行抓取
        result = scraper.scrape_article(str(request.url))
        
        if not result:
            error_msg = "抓取失败，未能获取到内容"
            logger.error(error_msg)
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )
        
        # 验证返回的数据
        if not result.get('title'):
            result['title'] = "未找到标题"
        
        if not result.get('content'):
            error_msg = "抓取的内容为空"
            logger.error(error_msg)
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )
        
        # 构建响应
        response = ScrapeResponse(
            title=result['title'],
            content=result['content'],
            video_link=result.get('video_link'),
            cover_image=result.get('cover_image'),
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"成功抓取文章: {result['title']}")
        return response
        
    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = f"抓取过程中出现错误: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )

@app.get("/")
async def root():
    """API根路径，返回服务信息"""
    return {
        "message": "欢迎使用文章抓取API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# 启动服务器配置
if __name__ == "__main__":
    uvicorn.run(
        "api:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 