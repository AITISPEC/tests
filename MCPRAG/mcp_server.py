#!/usr/bin/env python3
"""MCP-сервер для чтения wiki-файлов (тестовый)."""

import json
import sys
from pathlib import Path

# Форсируем UTF-8 на Windows
if sys.platform == "win32":
    try:
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
WIKI_DIR = ROOT / "wiki"
WIKI_DIR.mkdir(exist_ok=True)  # создаём, если нет


# ---------- Вспомогательные функции ----------
def _list_wiki_files():
    if not WIKI_DIR.exists():
        return []
    return [f.name for f in WIKI_DIR.iterdir() if f.is_file()]


def _read_wiki_file(filename: str) -> str:
    filepath = WIKI_DIR / filename
    # защита от обхода каталога
    if not filepath.resolve().is_relative_to(WIKI_DIR.resolve()):
        return "Ошибка: попытка выйти за пределы wiki"
    if not filepath.exists():
        return f"Файл {filename} не найден"
    return filepath.read_text(encoding="utf-8", errors="ignore")


def _search_wiki(query: str, limit: int = 3) -> str:
    """Простой поиск по ключевым словам (регистронезависимый)."""
    results = []
    if not WIKI_DIR.exists():
        return "Папка wiki не найдена"
    for filepath in WIKI_DIR.iterdir():
        if not filepath.is_file():
            continue
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        if query.lower() in content.lower():
            # Находим первое вхождение и вырезаем контекст
            idx = content.lower().find(query.lower())
            start = max(0, idx - 200)
            end = min(len(content), idx + len(query) + 200)
            fragment = content[start:end].strip()
            results.append(f"--- {filepath.name} ---\n{fragment}")
            if len(results) >= limit:
                break
    return "\n\n".join(results) if results else "Ничего не найдено."


# ---------- Описание инструментов ----------
TOOLS = [
    {
        "name": "list_wiki_files",
        "description": "Возвращает список имён всех файлов в папке wiki",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "read_wiki_file",
        "description": "Возвращает содержимое указанного файла из папки wiki",
        "inputSchema": {
            "type": "object",
            "properties": {"filename": {"type": "string", "description": "Имя файла"}},
            "required": ["filename"],
        },
    },
    {
        "name": "search_wiki",
        "description": "Ищет ключевые слова в файлах wiki и возвращает фрагменты (до 3)",
        "inputSchema": {
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
]


# ---------- Обработчик запросов ----------
def _tool_result_text(name: str, arguments: dict) -> str:
    if name == "list_wiki_files":
        return json.dumps(_list_wiki_files(), ensure_ascii=False)
    if name == "read_wiki_file":
        return _read_wiki_file(arguments.get("filename", ""))
    if name == "search_wiki":
        return _search_wiki(arguments.get("query", ""), arguments.get("limit", 3))
    raise ValueError(f"Unknown tool: {name}")


def handle(request: dict):
    method = request.get("method")
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "wiki-tools", "version": "1.0.0"},
            },
        }
    if method in ("notifications/initialized", "notifications/cancelled"):
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = request.get("params", {})
        try:
            text = _tool_result_text(params.get("name"), params.get("arguments", {}))
            result = {"content": [{"type": "text", "text": text}], "isError": False}
        except Exception as e:
            result = {"content": [{"type": "text", "text": str(e)}], "isError": True}
        return {"jsonrpc": "2.0", "id": req_id, "result": result}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    if req_id is not None:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
    return None


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except Exception:
            continue
        response = handle(request)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
