from fastapi import FastAPI
from blocklink.utils.block_api import BlackAPI

from blocklink.strategy.connect_strategy import ConnectStrategy
from blocklink.strategy.discover_strategy import DiscoverStrategy


app = FastAPI()
block_api = BlackAPI(app)

block_api.add_strategy(ConnectStrategy())
block_api.add_strategy(DiscoverStrategy())

block_api.open_api("ws")
block_api.open_api("node")
block_api.open_api("bridge")

block_api.init()
