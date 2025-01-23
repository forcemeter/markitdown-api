# Markitdown API

## 简介

Markitdown API 是一个用于文档的 API 服务。它提供了一系列功能来解析和转换 Markdown 文档。

## 部署

### 环境要求

- Python 3.x
- pip

### 安装步骤

1. 克隆项目仓库：

   ```bash
   git clone https://github.com/forcemeter/markitdown-api.git
   ```

2. 安装运行：

   ```bash
    python3.10 -m venv venv
    source venv/bin/activate
    pip3.10 install -r requirements.txt
    uvicorn main:app --reload
   ```

### 提交任务


1. 文件

```bash
curl -X POST http://127.0.0.1:8000/convert/url/ -H "Content-Type: application/json" -d '{"url": "tests/docx"}'
```


2. 链接

```bash
curl -X POST http://127.0.0.1:8000/convert/url/ -H "Content-Type: application/json" -d '{"url": "https://www.beijing.gov.cn/zhengce/zhengcefagui/202402/W020240226346416011070.pdf"}'
```


### 响应

正常响应

```json
{
   "code": 200,
   "filename": "文件路径",
   "markdown": "文本内容",
   "detail": "success"
}
```

异常响应

```json
{
   "detail": "错误信息",
}
```