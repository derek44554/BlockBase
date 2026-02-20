FROM python:3.13

# 设置工作目录
WORKDIR /app

# 安装系统依赖（如果需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 并安装依赖
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码（docker-compose 会用 volume 覆盖）
COPY . .

# 创建必要的目录
RUN mkdir -p /app/data /app/resources /app/config

# 暴露端口
EXPOSE 24001

# 指定启动命令，使用 Uvicorn 运行 FastAPI 应用
# 生产模式：多进程运行
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "24001", "--workers", "4"]

