import requests
from blocklink.utils.node_meta import NodeMeta

ipfs_api = NodeMeta()["ipfs_api"]


from fastapi import HTTPException


def add_file_to_ipfs(file_path):
    """
    上传文件
    :param file_path:
    :return:
    """
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{ipfs_api}/add", params={"pin": "true"}, files=files, timeout=60)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to add file to IPFS")
            result = response.json()
            return result['Hash']
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="IPFS add timeout")


def pin_cid(cid):
    """
    固定（pin）文件
    :param cid:
    :return:
    """
    try:
        response = requests.post(f"{ipfs_api}/pin/add", params={"arg": cid}, timeout=30)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to pin CID")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="IPFS pin timeout")


def list_pins():
    """
    pin文件的列表
    :return:
    """
    try:
        response = requests.post(f"{ipfs_api}/pin/ls", timeout=30)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to list pins")
        pins = response.json().get("Keys", {})
        return list(pins.keys())
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="IPFS list pins timeout")


def unpin_cid(cid):
    """
    取消pin
    :param cid:
    :return:
    """
    try:
        response = requests.post(f"{ipfs_api}/pin/rm", params={"arg": cid}, timeout=30)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to unpin CID")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="IPFS unpin timeout")


def garbage_collect():
    """
    垃圾回收
    :return:
    """
    try:
        response = requests.post(f"{ipfs_api}/repo/gc", timeout=300)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="IPFS garbage collection failed")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="IPFS gc timeout")


def get_file_chunk_from_ipfs(cid, chunk_size=1 * 1024 * 1024):
    # 通过 IPFS API 获取文件
    ipfs_url = f"{ipfs_api}/cat"
    try:
        response = requests.post(ipfs_url, params={"arg": cid}, timeout=30, stream=True)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="File not found on IPFS")

        content_length = response.headers.get('Content-Length')
        total_count = None
        if content_length:
            total_count = (int(content_length) + chunk_size - 1) // chunk_size

        return response.iter_content(chunk_size=chunk_size), total_count
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="IPFS cat timeout")

