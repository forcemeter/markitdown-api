from fastapi import FastAPI, UploadFile, File, HTTPException
from markitdown import MarkItDown
from pydantic import BaseModel
import shutil
import os
import hashlib
import logging
import requests
import traceback

app = FastAPI(title="MarkItDown API", description="Convert files or URLs to Markdown text.")

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file
        logging.StreamHandler()          # Log to the console
    ]
)

# 定义返回数据结构，声明每个字段的含义
class MarkdownResponse(BaseModel):
    code: int
    filename: str
    markdown: str
    detail: str


class URLRequest(BaseModel):
    url: str
    force_download: bool = False


def markdown(filename: str):
    """
    将指定文件转换为 Markdown 格式。
    支持文档: PDF, DOCX, XLSX, Images, etc.
    """
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="File not found")

    md = MarkItDown()
    try:
        result = md.convert(filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")

    text = ""
    if result:
        text = result.text_content

    return {"code": 200, "filename": filename, "markdown": text, "detail": "success"}


@app.post("/convert/file/", response_model=MarkdownResponse)
async def convert_file(file: UploadFile = File(...)):
    """
    上传文件并将其转换为 Markdown 格式。
    支持文档: PDF, DOCX, XLSX, Images, etc.
    """
    temp_file = None
    try:
        temp_file = f"temp_{file.filename}"
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return markdown(temp_file)

    except Exception as e:
        logging.error(f"File conversion error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        logging.info(f"Converted {temp_file} to Markdown")


@app.post("/convert/url/", response_model=MarkdownResponse)
async def convert_uri(request: URLRequest):
    """
    指定文件路径或者链接，并将其转换为 Markdown 格式。
    支持文档: PDF, DOCX, XLSX, Images, etc.

    参数:
    - url: str
      文件路径或链接。
    - force_download: bool
      如果为 True，则强制重新下载文件，即使文件已经存在。
    """
    url = request.url
    try:
        # 如果文件存在则直接读取
        if os.path.exists(url):
            md = MarkItDown()
            result = md.convert(url)
            return markdown(url)

        if not url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="Invalid URL. Must start with http:// or https://")

        # 下载链接到本地，以链接 md5hash 作为文件名
        temp_file = "tmp/" + hashlib.md5(url.encode("utf-8")).hexdigest()
        if not os.path.exists(temp_file) or request.force_download:
            logging.info(f"Download {url} to {temp_file}")
            header = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            }
            with requests.get(url, headers=header, stream=True) as r:
                r.raise_for_status()
                with open(temp_file, "wb") as f:
                    shutil.copyfileobj(r.raw, f)

        return markdown(temp_file)

    except requests.RequestException as req_err:
        raise HTTPException(status_code=400, detail=f"Request error: {str(req_err)}")
    except Exception as e:
        logging.error(f"File conversion error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        logging.info(f"Converted {url} to Markdown")