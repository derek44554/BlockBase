import base64
from blocklink.models.ins.ins_cert_factory import InsCertFactory
from blocklink.models.node.node import NodeModel
from blocklink.models.routers.route_block import RouteBlock
from blocklink.utils.send import execute_send_ins
from blocklink.models.ins.ins_cert import InsCert
from apps.ipfs.utils.ipfs_api import add_file_to_ipfs,  get_file_chunk_from_ipfs


file_route = RouteBlock(route="/file")

@file_route.cert("/get")
async def get_file(node_model: NodeModel, ins_cert: InsCert):
    """
    通过CID获取文件 分块传输
    :param node_model:
    :param ins_cert:
    :return:
    """
    # 通过CID 开始字节与结束字节进行索要 如果不存在就返回不存在的状态码
    cid = ins_cert.data["cid"]
    # 获取文件 分块
    file_data_chunks = get_file_chunk_from_ipfs(cid)
    for i, chunk in enumerate(file_data_chunks):
        print(f"Chunk {i}: {len(chunk)} bytes")
        data = {
            "cid": cid,
            "index": i,  # 索引 0 开始
            "data": base64.b64encode(chunk).decode('utf-8'),  # 数据
            "count": len(file_data_chunks),
        }
        ins_cert_factory = InsCertFactory()
        ins = ins_cert_factory.create(receiver=ins_cert.sender, routing="/res/file", data=data,
                                      status_code=None, res=ins_cert.bid)
        await execute_send_ins(ins=ins, is_res=False)

