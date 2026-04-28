from fastapi import FastAPI
from blocklink.utils.block_api import BlackAPI

from blocklink.strategy.connect_strategy import ConnectStrategy
from blocklink.strategy.discover_strategy import DiscoverStrategy

from utils.app_loader import load_apps

app = FastAPI()
block_api = BlackAPI(app)

# 注册项目 apps 目录中启用的 App
for route_app in load_apps():
    block_api.add_app(route_app)

block_api.add_strategy(ConnectStrategy())
block_api.add_strategy(DiscoverStrategy())

block_api.open_api("ws")
block_api.open_api("node")
block_api.open_api("bridge")

block_api.init()
