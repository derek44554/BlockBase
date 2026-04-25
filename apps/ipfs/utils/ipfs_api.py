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
        # Added timeout to prevent DoS via hung connections
        with requests.post(f"{ipfs_api}/add", params={"pin": "true"}, files=files, timeout=30) as response:
            if response.status_code != 200:
                raise Exception(f"IPFS add failed: {response.text}")
            result = response.json()
            return result['Hash']


def pin_cid(cid):
    """
    固定（pin）文件
    :param cid:
    :return:
    """
    # Added timeout to prevent DoS
    with requests.post(f"{ipfs_api}/pin/add", params={"arg": cid}, timeout=30) as response:
        if response.status_code != 200:
            raise Exception(f"IPFS pin failed: {response.text}")


def list_pins():
    """
    pin文件的列表
    :return:
    """
    # Added timeout to prevent DoS
    with requests.post(f"{ipfs_api}/pin/ls", timeout=30) as response:
        if response.status_code != 200:
            raise Exception(f"IPFS list pins failed: {response.text}")
        pins = response.json().get("Keys", {})
        return list(pins.keys())


def unpin_cid(cid):
    """
    取消pin
    :param cid:
    :return:
    """
    # Added timeout to prevent DoS
    with requests.post(f"{ipfs_api}/pin/rm", params={"arg": cid}, timeout=30) as response:
        if response.status_code != 200:
            raise Exception(f"IPFS unpin failed: {response.text}")


def garbage_collect():
    """
    垃圾回收
    :return:
    """
    # Added timeout to prevent DoS
    with requests.post(f"{ipfs_api}/repo/gc", timeout=60) as response:
        if response.status_code != 200:
            raise Exception(f"IPFS GC failed: {response.text}")


def get_file_chunk_from_ipfs(cid, chunk_size=1 * 1024 * 1024):
    """
    通过 IPFS API 获取文件
    """
    ipfs_url = f"{ipfs_api}/cat"
    # Use stream=True and timeout to prevent memory exhaustion and hung connections
    with requests.post(ipfs_url, params={"arg": cid}, stream=True, timeout=30) as response:
        if response.status_code != 200:
            raise Exception(f"IPFS cat failed: {response.text}")

        file_data_chunks = []
        # Built as a list to avoid breaking callers that expect indexing or len()
        # while still using streaming to safely process the response.
        for chunk in response.iter_content(chunk_size=chunk_size):
            file_data_chunks.append(chunk)

        return file_data_chunks

