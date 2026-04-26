import requests
from blocklink.utils.node_meta import NodeMeta

ipfs_api = NodeMeta()["ipfs_api"]


def add_file_to_ipfs(file_path):
    """
    上传文件
    :param file_path:
    :return:
    """
    with open(file_path, 'rb') as f:
        files = {'file': f}
        # Sentinel: Added timeout to prevent hanging connections
        response = requests.post(f"{ipfs_api}/add", params={"pin": "true"}, files=files, timeout=30)
        if response.status_code != 200:
            response.close()
            raise Exception(f"IPFS add failed with status {response.status_code}")
        result = response.json()
        response.close()
        return result['Hash']


def pin_cid(cid):
    """
    固定（pin）文件
    :param cid:
    :return:
    """
    # Sentinel: Added timeout to prevent hanging connections
    response = requests.post(f"{ipfs_api}/pin/add", params={"arg": cid}, timeout=30)
    if response.status_code != 200:
        response.close()
        raise Exception(f"IPFS pin/add failed with status {response.status_code}")
    response.close()


def list_pins():
    """
    pin文件的列表
    :return:
    """
    # Sentinel: Added timeout to prevent hanging connections
    response = requests.post(f"{ipfs_api}/pin/ls", timeout=30)
    if response.status_code != 200:
        response.close()
        raise Exception(f"IPFS pin/ls failed with status {response.status_code}")
    pins = response.json().get("Keys", {})
    response.close()
    return list(pins.keys())


def unpin_cid(cid):
    """
    取消pin
    :param cid:
    :return:
    """
    # Sentinel: Added timeout to prevent hanging connections
    response = requests.post(f"{ipfs_api}/pin/rm", params={"arg": cid}, timeout=30)
    if response.status_code != 200:
        response.close()
        raise Exception(f"IPFS pin/rm failed with status {response.status_code}")
    response.close()


def garbage_collect():
    """
    垃圾回收
    :return:
    """
    # Sentinel: Added timeout to prevent hanging connections
    response = requests.post(f"{ipfs_api}/repo/gc", timeout=30)
    if response.status_code != 200:
        response.close()
        raise Exception(f"IPFS repo/gc failed with status {response.status_code}")
    response.close()


def get_file_chunk_from_ipfs(cid, chunk_size=1 * 1024 * 1024):
    # 通过 IPFS API 获取文件
    ipfs_url = f"{ipfs_api}/cat"
    # Sentinel: Added stream=True and timeout to prevent DoS via OOM or hanging connections
    response = requests.post(ipfs_url, params={"arg": cid}, stream=True, timeout=30)

    if response.status_code != 200:
        response.close()
        raise Exception(f"IPFS cat failed with status {response.status_code}")

    file_data_chunks = []

    # Sentinel: Use iter_content to stream the response into chunks without loading all at once in 'response.content'
    # We still return a list to avoid breaking existing callers that expect len()
    try:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                file_data_chunks.append(chunk)
    finally:
        response.close()

    return file_data_chunks

