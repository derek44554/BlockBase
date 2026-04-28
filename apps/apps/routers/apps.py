from blocklink.models.ins.ins_cert import InsCert
from blocklink.models.node.node import NodeModel
from blocklink.models.routers.route_block import RouteBlock
from blocklink.utils.ins_except import InsCertException

from apps.apps.utils.local_apps_manager import LocalAppsManager

apps_route = RouteBlock(route="/apps")


@apps_route.cert("/all")
async def apps_cert(node_model: NodeModel, ins_cert: InsCert):
    return {"items":LocalAppsManager().response()}


@apps_route.cert("/disable")
async def apps_disable_cert(node_model: NodeModel, ins_cert: InsCert):
    """
    关闭本地插件模块。
    data.name 为 module.yml 中声明的插件名称，修改后会重启 FastAPI。
    :param node_model:
    :param ins_cert:
    :return:
    """
    name = ins_cert.data.get("name")

    if not isinstance(name, str) or not name:
        raise InsCertException(
            node=node_model,
            ins_cert=ins_cert,
            status_code=42,
            content="Incorrect app name",
        )

    try:
        return LocalAppsManager().disable(name)
    except FileNotFoundError as exception:
        raise InsCertException(
            node=node_model,
            ins_cert=ins_cert,
            status_code=31,
            content=f"App not found: {exception}",
        )


@apps_route.cert("/enable")
async def apps_enable_cert(node_model: NodeModel, ins_cert: InsCert):
    """
    开启本地插件模块。
    data.name 为 module.yml 中声明的插件名称，修改后会重启 FastAPI。
    :param node_model:
    :param ins_cert:
    :return:
    """
    name = ins_cert.data.get("name")

    if not isinstance(name, str) or not name:
        raise InsCertException(
            node=node_model,
            ins_cert=ins_cert,
            status_code=42,
            content="Incorrect app name",
        )

    try:
        return LocalAppsManager().enable(name)
    except FileNotFoundError as exception:
        raise InsCertException(
            node=node_model,
            ins_cert=ins_cert,
            status_code=31,
            content=f"App not found: {exception}",
        )
