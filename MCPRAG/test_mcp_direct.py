#!/usr/bin/env python3
"""Прямой вызов MCP-сервера filesystem для поиска в bio_env."""

import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Укажите ту же папку, что в настройках MCP (ALLOWED_DIRECTORIES)
WIKI_DIR = Path(r"D:\ProjectsGH\valiDATAr\bio_env\wiki")


async def search_in_files(query: str, limit: int = 3) -> str:
    """Ищет query в текстовых файлах внутри WIKI_DIR."""
    # 1. Запускаем MCP-сервер (как это делает LM Studio)
    params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", str(WIKI_DIR)],
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 2. Получаем список файлов в папке
            result = await session.call_tool("list_directory", {"path": str(WIKI_DIR)})
            # ✅ ИСПРАВЛЕНИЕ: list_directory возвращает текст, а не JSON
            text_content = result.content[0].text if result.content else ""
            files = [line.strip() for line in text_content.splitlines() if line.strip()]

            # Оставляем только текстовые файлы
            text_files = [f for f in files if not f.startswith("[DIR]")]

            if not text_files:
                return "В папке нет текстовых файлов."

            found = []
            for fname in text_files:
                # 3. Читаем каждый файл
                filepath = WIKI_DIR / fname
                result = await session.call_tool("read_file", {"path": str(filepath)})
                content = result.content[0].text if result.content else ""

                # 4. Ищем запрос (регистронезависимо)
                if query.lower() in content.lower():
                    # Вырезаем кусок вокруг первого вхождения
                    idx = content.lower().find(query.lower())
                    start = max(0, idx - 200)
                    end = min(len(content), idx + len(query) + 200)
                    fragment = content[start:end].strip()
                    found.append(f"--- {fname} ---\n{fragment}")
                    if len(found) >= limit:
                        break

            return "\n\n".join(found) if found else "Ничего не найдено."


async def main():
    print("Поиск по файлам в папке bio_env/wiki")
    query = input("Введите запрос: ").strip()
    if not query:
        print("Default query: закон Ома")
        query = "закон Ома"
    result = await search_in_files(query)
    print("\nРезультат:\n")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
