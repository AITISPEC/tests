#!/usr/bin/env python3
"""Отладка MCP: посмотреть, что находится в папке bio_env."""

import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

WIKI_DIR = Path(r"D:\ProjectsGH\valiDATAr\bio_env\wiki")


async def debug_list():
    params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", str(WIKI_DIR)],
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Получаем список содержимого корневой папки
            result = await session.call_tool("list_directory", {"path": str(WIKI_DIR)})
            text = result.content[0].text if result.content else ""
            files = [line.strip() for line in text.splitlines() if line.strip()]
            print("Содержимое папки:", WIKI_DIR)
            for f in files:
                print("  -", f)


async def main():
    await debug_list()


if __name__ == "__main__":
    asyncio.run(main())
