import asyncio
from fastmcp import Client

async def main():
    async with Client("src/main.py") as c:          # spawns python src/main.py over stdio
        print([t.name for t in await c.list_tools()])
        r = await c.call_tool("get_company_news", {"symbol": "AAPL", "days": 3})
        print(r.structured_content)
