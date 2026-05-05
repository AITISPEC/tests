# Dump: ROOT FILES

**Root:** `C:\Users\AITISPEC\PycharmProjects\klaim`

---

## 📄 AITISPEC-dump_for_ai.py

```py
import os
from pathlib import Path

def dump_project(root: str = ".", limit_mb: float = 0.8):
	root_path = Path(root).resolve()
	skip_dirs = {'.git', '__pycache__', '.venv', 'venv', '.pytest_cache', '.mypy_cache', 'output', 'models', 'node_modules'}
	skip_ext = {'.parquet', '.feather', '.pkl', '.pickle', '.h5', '.hdf5', '.arrow', '.xlsx', '.xls', '.pyc', '.pyd', '.dll', '.exe', '.zip', '.tar.gz'}
	limit_bytes = int(limit_mb * 1024 * 1024)

	def _collect_dir(base_dir: Path) -> str:
		lines = [f"# Dump: {base_dir.name}\n\n", f"**Root:** `{base_dir}`\n\n---\n\n"]
		for dirpath, dirnames, filenames in os.walk(base_dir):
			dirnames[:] = [d for d in dirnames if d not in skip_dirs and not d.startswith('.')]
			for fname in sorted(filenames):
				fpath = Path(dirpath) / fname
				rel = fpath.relative_to(base_dir)

				if fpath.suffix.lower() in skip_ext:
					lines.append(f"- `[SKIP BIN] {rel}`\n")
					continue
				if fpath.stat().st_size > limit_bytes:
					lines.append(f"- `[SKIP LARGE] {rel}` ({fpath.stat().st_size/1024/1024:.1f} MB)\n")
					continue
				try:
					content = fpath.read_text(encoding='utf-8', errors='replace')
					lang = fpath.suffix.lower().lstrip('.') or 'text'
					lines.append(f"## 📄 {rel}\n\n```{lang}\n{content.rstrip()}\n```\n\n---\n\n")
				except Exception as e:
					lines.append(f"- `[ERROR READ] {rel}`: {e}\n")
		return "".join(lines)

	# 1. Дамп файлов корня
	root_lines = ["# Dump: ROOT FILES\n\n", f"**Root:** `{root_path}`\n\n---\n\n"]
	for fname in sorted([f for f in root_path.iterdir() if f.is_file() and f.name != "dump_for_ai.py"]):
		if fname.name.startswith('.'): continue
		if fname.suffix.lower() in skip_ext:
			root_lines.append(f"- `[SKIP BIN] {fname.name}`\n")
			continue
		if fname.stat().st_size > limit_bytes:
			root_lines.append(f"- `[SKIP LARGE] {fname.name}`\n")
			continue
		try:
			content = fname.read_text(encoding='utf-8', errors='replace')
			lang = fname.suffix.lower().lstrip('.') or 'text'
			root_lines.append(f"## 📄 {fname.name}\n\n```{lang}\n{content.rstrip()}\n```\n\n---\n\n")
		except Exception as e:
			root_lines.append(f"- `[ERROR READ] {fname.name}`: {e}\n")

	(root_path / "dump_root.md").write_text("".join(root_lines), encoding='utf-8')
	print("✅ Created: dump_root.md")

	# 2. Дампы папок первого уровня
	for item in sorted(root_path.iterdir()):
		if item.is_dir() and item.name not in skip_dirs and not item.name.startswith('.'):
			content = _collect_dir(item)
			(root_path / f"dump_{item.name}.md").write_text(content, encoding='utf-8')
			print(f"✅ Created: dump_{item.name}.md")

	print("Готово. Дампы сгенерированы.")

if __name__ == "__main__":
	dump_project()
```

---

## 📄 config.yaml

```yaml
name: klaim-func
runtime: python314
entrypoint: index.handler
memory: 128m
execution_timeout: 3s
min_log_level: WARN
service_account_id: aje1b2qe9648j662fsvn
env:
  YDB_ENDPOINT: grpcs://ydb.serverless.yandexcloud.net:2135
  YDB_DATABASE: /ru-central1/b1g36pu3komilp48v4aq/etnkcomgii27j57bhkmu
  YDB_TABLE_NAME: user_inboxes
lockbox_keys: []
```

---

## 📄 CREATE TABLE user_inboxes.txt

```txt
CREATE TABLE user_inboxes
(
    `recipient_id` Uint32 NOT NULL,
    `message_id` Uint32 NOT NULL,
    `sender_id` Uint32 NOT NULL,
    `text` Utf8 NOT NULL,
    `created_at` Timestamp NOT NULL,
    `status` Utf8,
    PRIMARY KEY (`recipient_id`, `message_id`)
)
WITH (
    AUTO_PARTITIONING_BY_SIZE = ENABLED,
    AUTO_PARTITIONING_BY_LOAD = ENABLED,
    AUTO_PARTITIONING_PARTITION_SIZE_MB = 512,
    AUTO_PARTITIONING_MIN_PARTITIONS_COUNT = 1,
    TTL = Interval("P7D") ON `created_at`,
    KEY_BLOOM_FILTER = ENABLED
);
```

---

## 📄 deploy.py

```py
#!/usr/bin/env python3
import os
import sys
import subprocess
import zipfile
import tempfile
import time
import yaml
from pathlib import Path
from typing import Dict, Any


class ChatDeployer:
    def __init__(self, folder_id: str = None):
        # Проверка yc CLI
        try:
            subprocess.run(['yc', '--version'], capture_output=True, check=True)
        except:
            print("❌ yc CLI не установлен")
            sys.exit(1)

        if not folder_id:
            result = subprocess.run(['yc', 'config', 'get', 'folder-id'],
                                    capture_output=True, text=True)
            self.folder_id = result.stdout.strip()
        else:
            self.folder_id = folder_id

    def create_zip(self, source_dir: Path) -> Path:
        """Создание zip с кодом функции, включая подпапки"""
        zip_path = Path(tempfile.gettempdir()) / f"chat-function-{int(time.time())}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = Path(root) / file
                    # Пропускаем ненужные файлы
                    if file in ['.env', '.gitignore', '.zipignor']:
                        continue
                    # Относительный путь внутри архива
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)

        print(f"✅ Архив создан: {zip_path}")
        return zip_path

    def deploy(self, config: Dict[str, Any], source_dir: Path, secret_id: str = None):
        """Деплой функции"""
        zip_path = self.create_zip(source_dir)

        cmd = [
            'yc', 'serverless', 'function', 'version', 'create',
            '--function-name', config['name'],
            '--runtime', config['runtime'],
            '--entrypoint', config['entrypoint'],
            '--memory', str(config['memory']),
            '--execution-timeout', str(config['execution_timeout']),
            '--source-path', str(zip_path)
        ]

        if config.get('service_account_id'):
            cmd.extend(['--service-account-id', config['service_account_id']])

        if secret_id and config.get('lockbox_keys'):
            for key in config['lockbox_keys']:
                cmd += ['--secret', f'id={secret_id},key={key},environment-variable={key}']

        if config.get('env'):
            env_str = ','.join([f"{k}={v}" for k, v in config['env'].items()])
            cmd.extend(['--environment', env_str])

        print("🚀 Деплой...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        zip_path.unlink()  # удаляем временный файл

        if result.returncode == 0:
            print("✅ Функция задеплоена")
            return True
        else:
            print(f"❌ Ошибка: {result.stderr}")
            return False


def main():
    # Читаем конфиг из YAML
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    print("📦 Конфигурация загружена:")
    print(f"   Функция: {config['name']}")
    print(f"   Переменные окружения: {list(config.get('env', {}).keys())}")

    deployer = ChatDeployer()
    deployer.deploy(config, Path('./deploy'))  # папка с кодом функции


if __name__ == '__main__':
    main()
```

---

## 📄 raw_ydb.txt

```txt
DEBUG: raw event={"httpMethod": "POST", "headers": {"Accept": "*/*", "Content-Length": "59", "Content-Type": "application/json", "Host": "d5drpq0l7ovt2gipaa7e.y5sm01em.apigw.yandexcloud.net", "Traceparent": "00-00000000000000004b6d620f806b5961-8c86bc80a6471bea-01", "Tracestate": "", "Uber-Trace-Id": "4b6d620f806b5961:4069cffe0b689c13:24c1e203283afe9a:1", "User-Agent": "curl/8.18.0", "X-Api-Gateway-Function-Id": "d4eso3p6o2kgt8ok6hpp", "X-Envoy-External-Address": "81.4.209.249", "X-Envoy-Original-Path": "/api/send", "X-Forwarded-For": "81.4.209.249", "X-Forwarded-Proto": "https", "X-Real-Remote-Address": "81.4.209.249:55694", "X-Request-Id": "c1f1ffd8-229a-4109-99bb-ecf6e5197991", "X-Serverless-Certificate-Ids": "{}", "X-Serverless-Gateway-Id": "d5drpq0l7ovt2gipaa7e", "X-Trace-Id": "6fa88461-2b19-45b6-afcb-55de25e07f66"}, "url": "/api/send?", "params": {}, "multiValueParams": {}, "pathParams": {}, "multiValueHeaders": {"Accept": ["*/*"], "Content-Length": ["59"], "Content-Type": ["application/json"], "Host": ["d5drpq0l7ovt2gipaa7e.y5sm01em.apigw.yandexcloud.net"], "Traceparent": ["00-00000000000000004b6d620f806b5961-8c86bc80a6471bea-01"], "Tracestate": [""], "Uber-Trace-Id": ["4b6d620f806b5961:4069cffe0b689c13:24c1e203283afe9a:1"], "User-Agent": ["curl/8.18.0"], "X-Api-Gateway-Function-Id": ["d4eso3p6o2kgt8ok6hpp"], "X-Envoy-External-Address": ["81.4.209.249"], "X-Envoy-Original-Path": ["/api/send"], "X-Forwarded-For": ["81.4.209.249"], "X-Forwarded-Proto": ["https"], "X-Real-Remote-Address": ["81.4.209.249:55694"], "X-Request-Id": ["c1f1ffd8-229a-4109-99bb-ecf6e5197991"], "X-Serverless-Certificate-Ids": ["{}"], "X-Serverless-Gateway-Id": ["d5drpq0l7ovt2gipaa7e"], "X-Trace-Id": ["6fa88461-2b19-45b6-afcb-55de25e07f66"]}, "queryStringParameters": {}, "multiValueQueryStringParameters": {}, "requestContext": {"identity": {"sourceIp": "81.4.209.249", "userAgent": "curl/8.18.0"}, "httpMethod": "POST", "requestId": "c1f1ffd8-229a-4109-99bb-ecf6e5197991", "requestTime": "29/Mar/2026:21:28:01 +0000", "requestTimeEpoch": 1774819681}, "body": "{\"sender_id\":\"user1\",\"recipient_id\":\"user2\",\"text\":\"Hello\"}", "isBase64Encoded": false, "path": "/api/send"}
```

---

## 📄 requirements.txt

```txt
requests
pyyaml
ydb
```

---

## 📄 test.sh

```sh
#!/bin/bash

API_URL="https://d5drpq0l7ovt2gipaa7e.y5sm01em.apigw.yandexcloud.net/api/send"

echo "=== Тестирование HTTP‑запросов ==="
echo "Тестируемый URL: $API_URL"
echo "=========================================="

# Тест 1: Полный JSON payload (в body)
echo -e "\n--- Тест 1: Полный JSON в body ---"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"body": {"recipient_id": 2, "message_id": 1, "sender_id": 3}}' \
  -w "\nHTTP Status: %{http_code}\n" \
  --silent

# Тест 2: JSON‑строка в body
echo -e "\n--- Тест 2: JSON‑строка в body ---"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"body": "{\"recipient_id\": 2, \"message_id\": 1, \"sender_id\": 3}"}' \
  -w "\nHTTP Status: %{http_code}\n" \
  --silent

# Тест 3: Неполный JSON в body
echo -e "\n--- Тест 3: Неполный JSON в body ---"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"body": {"recipient_id": 2, "message_id": 1}}' \
  -w "\nHTTP Status: %{http_code}\n" \
  --silent

# Тест 4: Пустой body
echo -e "\n--- Тест 4: Пустой JSON в body ---"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"body": {}}' \
  -w "\nHTTP Status: %{http_code}\n" \
  --silent

read -r
```

---

