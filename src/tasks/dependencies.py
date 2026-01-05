import aiohttp
from fastapi import Request
from taskiq import TaskiqDepends


async def get_client(request: Request = TaskiqDepends()) -> aiohttp.ClientSession:
    return request.app.state.aiohttp_client
