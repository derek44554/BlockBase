import hashlib
import os
import secrets
import tempfile
from pathlib import Path

import requests
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from apps.block.utils.block import BlockDB
from apps.block.utils.db_block import engine
from apps.ipfs.utils.ipfs_api import add_file_to_ipfs, ipfs_api, pin_cid

ipfs_fast_api = APIRouter()


@ipfs_fast_api.get("/{cid}", summary='获取IPFS文件')
async def get_file(cid: str):
    """
    获取IPFS文件
    """
    # Fetch the file data from IPFS
    response = requests.post(f"{ipfs_api}/cat", params={"arg": cid})

    # If the request fails, raise an error
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="File not found on IPFS")

    # 使用 StreamingResponse 返回文件流
    return StreamingResponse(
        response.iter_content(chunk_size=8192),  # 分块传输
        status_code=200
    )


@ipfs_fast_api.post("/upload", summary="上传文件并固定到 IPFS")
async def upload_file(password: str = Form(...), file: UploadFile = File(...)):
    """
    接收上传文件，保存到临时目录后上传并固定至 IPFS。
    """
    ipfs_password = os.getenv("IDENTITY")

    if ipfs_password is None:
        raise HTTPException(status_code=403, detail="没有设置IPFS密码")

    ipfs_password = hashlib.sha3_256(ipfs_password.encode()+"IPFS".encode('utf-8')).hexdigest()

    if not secrets.compare_digest(password, ipfs_password):
        raise HTTPException(status_code=403, detail="密码错误")

    if file.filename is None:
        raise HTTPException(status_code=400, detail="文件名缺失")

    try:
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="文件内容为空")
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)

        cid = add_file_to_ipfs(str(tmp_path))
        pin_cid(cid)

        return {"cid": cid}
    except HTTPException:
        raise
    except Exception:
        # Don't leak internal error details to the user
        raise HTTPException(status_code=500, detail="上传失败")
    finally:
        try:
            if 'tmp_path' in locals() and tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass
