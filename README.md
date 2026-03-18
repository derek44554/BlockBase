# BlockBase

> Block生态的基础项目


## ✨ 功能特性

保存自己的个人数据

[客户端](https://github.com/derek44554/block_box/releases)

[介绍视频](https://www.bilibili.com/video/BV18PwezvE6w/)

## 🚀 快速开始

### 前置要求

- Python 3.8+
- Docker & Docker Compose
- pip 包管理器

### 安装依赖

```bash
pip install blocklink
```

## 🔐 密钥配置

### 步骤 1: 生成顶级密钥对

> ⚠️ 如果已经生成过顶级密钥，可以跳过此步骤

顶级密钥用于控制和授权所有节点，请妥善保管。

```python
from blocklink.adapters.key.key_loot import generate_and_save_rsa_keys

# 生成顶级密钥对
generate_and_save_rsa_keys()
```

**生成文件：**
- `private_key_top.pem` - 顶级私钥（请勿泄露）
- `public_key_top.pem` - 顶级公钥

### 步骤 2: 生成节点密钥对与授权证书

```python
from blocklink.adapters.key.key_loot import generate_node

# 使用顶级私钥生成节点密钥
generate_node(private_key_top_path="private_key_top.pem")
```

**生成文件：**
- `node.yml` - 节点信息
- `signature.yml` - 授权证书（由顶级私钥签名授权）
- `private_key.pem` - 节点私钥（请勿泄露）
- `public_key.pem` - 节点公钥

## 📦 部署指南

### 1. 克隆项目

```bash
git clone https://github.com/derek44554/BlockBase.git
```

### 2. 配置文件放置

将生成的密钥和配置文件放置到指定目录：

```
BlockBase/
├── node.yml                     # 节点配置
└── resources/
    ├── private_key.pem          # 节点私钥
    ├── public_key.pem           # 节点公钥
    ├── public_key_top.pem       # 顶级公钥
    └── signature.yml            # 授权证书
```

### 3. 启动服务

> 💡 确保在 BlockBase 项目根目录下执行以下命令

```bash
# 创建网络
docker network create block

# 启动 Docker 容器
docker-compose up -d
```

### 4. 验证部署

服务启动后，访问以下地址：

- 本地访问：`http://localhost:24001`
- 局域网访问：`http://<局域网IP>:24001`
- 公网访问：`http://<公网IP>:24001`

## 🔧 使用说明

### 更新代码后重新部署

```bash
# 停止并删除旧容器，重新构建镜像
docker-compose down
docker-compose up -d --build
```

---
## 图片上传对接

### IPFS配置

文件是存储在IPFS里的

#### 创建IPFS容器

```shell
# 创建 IPFS 容器
docker run -d \
  --name ipfs \
  --restart always \
  --network block \
  -v /home/IPFS:/data/ipfs \
  -p 4001:4001 \
  -p 8080:8080 \
  -p 127.0.0.1:5001:5001 \
  -e IPFS_PATH=/data/ipfs \
  ipfs/go-ipfs:latest \
  daemon --migrate=true --agent-version-suffix=docker
```

IPFS 持久化默认目录在 `/home/IPFS`

#### 节点对接

在节点的`node.yml`文件里添加

```yaml
ipfs_api: http://ipfs:5001/api/v0
```

### .env 配置

在项目目录里创建.env文件

#### App配置密钥

用于App端进行配置的密钥

```text
IDENTITY=App配置密钥
```

生成App配置密钥

```python
import os
import base64

random_bytes = os.urandom(32)
# 你的App配置密钥
b64_token = base64.b64encode(random_bytes).decode("utf-8")
```

---
## 📄 许可证

详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**注意：** 请妥善保管所有私钥文件，切勿上传到公共仓库或分享给他人。


