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
        # ✅ FIX: Use params argument to prevent URL manipulation and parameter injection
        response = requests.post(f"{ipfs_api}/add", params={'pin': 'true'}, files=files)
        if response.status_code != 200:
            raise
        result = response.json()
        return result['Hash']


def pin_cid(cid):
    """
    固定（pin）文件
    :param cid:
    :return:
    """
    # ✅ FIX: Use params argument to prevent URL manipulation and parameter injection
    response = requests.post(f"{ipfs_api}/pin/add", params={'arg': cid})
    if response.status_code != 200:
        raise


def list_pins():
    """
    pin文件的列表
    :return:
    """
    response = requests.post(f"{ipfs_api}/pin/ls")
    if response.status_code != 200:
        raise
    pins = response.json().get("Keys", {})
    return list(pins.keys())


def unpin_cid(cid):
    """
    取消pin
    :param cid:
    :return:
    """
    # ✅ FIX: Use params argument to prevent URL manipulation and parameter injection
    response = requests.post(f"{ipfs_api}/pin/rm", params={'arg': cid})
    if response.status_code != 200:
        raise


def garbage_collect():
    """
    垃圾回收
    :return:
    """
    response = requests.post(f"{ipfs_api}/repo/gc")
    if response.status_code != 200:
        raise


def get_file_chunk_from_ipfs(cid, chunk_size=1 * 1024 * 1024):
    # 通过 IPFS API 获取文件
    # ✅ FIX: Use params argument to prevent URL manipulation and parameter injection
    ipfs_url = f"{ipfs_api}/cat"
    response = requests.post(ipfs_url, params={'arg': cid})

    if response.status_code != 200:
        raise

    file_data_chunks = []

    # 按块大小分割内容并存储到列表
    for i in range(0, len(response.content), chunk_size):
        chunk = response.content[i:i + chunk_size]
        file_data_chunks.append(chunk)

    return file_data_chunks

