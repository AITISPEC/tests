#!/usr/bin/env python3
"""Тест MCP-инструментов через Bionic API."""

import asyncio
import json

import aiohttp

URL = "http://localhost:1234/v1/chat/completions"
API_KEY = "sk-lm-HUYCmMP4:q8pXOaRtdDpQaSThqzQz"  # ваш ключ
MODEL = "bionic-agent"

# Инструмент, который мы хотим вызвать (должен совпадать с тем, что в MCP-сервере)
TOOL = {
    "type": "function",
    "function": {
        "name": "search_wiki",
        "description": "Ищет фрагменты документов по запросу в справочнике",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Поисковый запрос"},
                "limit": {
                    "type": "integer",
                    "description": "Максимум результатов",
                    "default": 3,
                },
            },
            "required": ["query"],
        },
    },
}


async def test_search(query: str):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": f"Найди в справочнике информацию по запросу: {query}. Если ничего нет, скажи, что не найдено.",
            }
        ],
        "tools": [TOOL],
        "tool_choice": {"type": "function", "function": {"name": "search_wiki"}},
        "temperature": 0.0,
        "stream": False,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            URL, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=60)
        ) as resp:
            if resp.status != 200:
                print(f"Ошибка HTTP {resp.status}: {await resp.text()}")
                return
            data = await resp.json()
            msg = data["choices"][0]["message"]

            # Проверяем, вызван ли инструмент
            if msg.get("tool_calls"):
                for tc in msg["tool_calls"]:
                    func = tc["function"]
                    if func["name"] == "search_wiki":
                        args = json.loads(func["arguments"])
                        print(f"✅ Инструмент вызван с аргументами: {args}")
                        # Здесь должен быть результат вызова, но в ответе от Bionic мы увидим
                        # только content модели, которая, скорее всего, вернёт результат.
                        # Если Bionic сам выполнил инструмент, то результат будет в content.
                        if msg.get("content"):
                            print("Результат от модели:")
                            print(msg["content"])
                        else:
                            print("Модель не вернула content после вызова инструмента.")
                    else:
                        print(f"⚠️ Вызван другой инструмент: {func['name']}")
            else:
                # Если инструмент не вызван, покажем content
                print("Инструмент не вызван. Content:")
                print(msg.get("content", ""))


async def main():
    print("Тест MCP-инструмента search_wiki")
    query = input("Введите поисковый запрос: ").strip()
    if not query:
        query = "закон Ома"
    await test_search(query)


if __name__ == "__main__":
    asyncio.run(main())
