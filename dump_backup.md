# Dump: backup

**Root:** `C:\Users\AITISPEC\PycharmProjects\klaim\backup`

---

## 📄 test.sh

```sh
curl https://d5drpq0l7ovt2gipaa7e.y5sm01em.apigw.yandexcloud.net/api/poll
read -r
```

---

## 📄 deploy\config.py

```py
import os


class Config:
    YDB_ENDPOINT = os.getenv("YDB_ENDPOINT")
    YDB_DATABASE = os.getenv("YDB_DATABASE")

    @property
    def YDB_TABLE_PATH(self):
        return f"{self.YDB_DATABASE}/user_inboxes"
```

---

## 📄 deploy\index.py

```py
# index.py

from handlers import send, poll, ack

import json


def handler(event, context):

    if event is None:
        event = {}

    method = event.get('httpMethod')
    path = (event.get('url') or event.get('path', '')).split('?')[0]
    body = event.get('body')

    # CORS preflight
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': 'https://sokol-mea.sourcecraft.site',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }

    if body:
        try:
            body = json.loads(body)
        except:
            body = {}

    query_params = event.get('queryStringParameters') or {}

    if method == 'POST' and path == '/api/send':
        result = send.handle(body)
    elif method == 'GET' and path == '/api/poll':
        recipient_id = query_params.get('recipient_id')
        last_id = query_params.get('last_id', '')
        result = poll.handle(recipient_id, last_id)
    elif method == 'POST' and path == '/api/ack':
        result = ack.handle(body)
    else:
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Origin': 'https://sokol-mea.sourcecraft.site'
            },
            'body': json.dumps({'error': 'Not found'})
        }

    if isinstance(result, tuple):
        response, status = result
    else:
        response, status = result, 200

    return {
        'statusCode': status,
        'headers': {
            'Access-Control-Allow-Origin': 'https://sokol-mea.sourcecraft.site',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(response)
    }
```

---

## 📄 deploy\requirements.txt

```txt
ydb==3.26.6
```

---

## 📄 deploy\ydb_client.py

```py
# ydb_client.py
import os
import ydb
import ydb.iam


class YDBClient:
    def __init__(self):
        self.endpoint = os.getenv('YDB_ENDPOINT')
        self.database = os.getenv('YDB_DATABASE')

        self.driver = ydb.Driver(
            endpoint=self.endpoint,
            database=self.database,
            credentials=ydb.iam.MetadataUrlCredentials(),
        )
        self.driver.wait(fail_fast=True, timeout=5)
        self.pool = ydb.SessionPool(self.driver)
        print("YDB Client Initialized")

    def execute(self, query, params=None):
        def _execute_query(session):
            return session.transaction().execute(
                query,
                parameters=params or {},
                commit_tx=True
            )

        return self.pool.retry_operation_sync(_execute_query)


ydb_client = YDBClient()
```

---

## 📄 deploy\handlers\__init__.py

```py

```

---

## 📄 deploy\handlers\ack.py

```py
# handlers/ack.py
from ydb_client import ydb_client
import ydb
import uuid
from config import Config
import json

config = Config()

def handle(data):
    if not data or 'recipient_id' not in data or 'message_ids' not in data:
        return {"error": "Missing fields"}, 400

    message_ids = data['message_ids']
    if not isinstance(message_ids, list) or len(message_ids) == 0:
        return {"error": "message_ids must be non-empty list"}, 400

    # Ограничим количество, чтобы не превысить лимит YDB на параметры
    if len(message_ids) > 100:
        return {"error": "Too many message_ids (max 100)"}, 400

    placeholders = ', '.join([f'$msg_{i}' for i in range(len(message_ids))])
    declarations = ''.join([f'DECLARE $msg_{i} AS Utf8; ' for i in range(len(message_ids))])

    query = f"""
        DECLARE $recipient_id AS Utf8;
        {declarations}

        DELETE FROM `{config.YDB_TABLE_PATH}`
        WHERE recipient_id = $recipient_id AND message_id IN ({placeholders});
    """

    # ВСЕ ключи с $ (единообразно!)
    params = {'$recipient_id': str(data['recipient_id'])}
    for i, msg_id in enumerate(message_ids):
        params[f'$msg_{i}'] = str(msg_id)  # ← Добавлен $

    try:
        ydb_client.execute(query, params)
        return {"status": "acknowledged", "deleted_count": len(message_ids)}, 200
    except Exception as e:
        return {"error": str(e)}, 500
```

---

## 📄 deploy\handlers\poll.py

```py
# handlers/poll.py
from ydb_client import ydb_client
import ydb
import uuid
from config import Config
import json

config = Config()


def handle(recipient_id, last_id=None):
    if not recipient_id:
        return {"error": "recipient_id required"}, 400

    # Если last_id пустой — выбираем все новые сообщения
    if not last_id:
        where_clause = "recipient_id = $recipient_id AND status = 'new'"
        params = {
            '$recipient_id': str(recipient_id)
        }
    else:
        where_clause = "recipient_id = $recipient_id AND message_id > $last_id AND status = 'new'"
        params = {
            '$recipient_id': str(recipient_id),
            '$last_id': str(last_id)
        }

    query = f"""
        DECLARE $recipient_id AS Utf8;
        {"DECLARE $last_id AS Utf8;" if last_id else ""}

        SELECT message_id, sender_id, text, created_at
        FROM `{config.YDB_TABLE_PATH}`
        WHERE {where_clause}
        ORDER BY created_at
        LIMIT 100;
    """

    try:
        result = ydb_client.execute(query, params)

        messages = []
        # Безопасная проверка результата
        if result and len(result) > 0 and result[0].rows:
            for row in result[0].rows:
                # Безопасное получение created_at
                created_at = row.created_at
                if hasattr(created_at, 'isoformat'):
                    created_at = created_at.isoformat()
                else:
                    created_at = str(created_at)

                messages.append({
                    "message_id": row.message_id,
                    "sender_id": row.sender_id,
                    "text": row.text,
                    "created_at": created_at
                })

        return {"messages": messages}, 200

    except Exception as e:
        return {"error": str(e)}, 500
```

---

## 📄 deploy\handlers\send.py

```py
# handlers/send.py
from ydb_client import ydb_client
import ydb
import uuid
from config import Config


config = Config()

def handle(data, context=None):
    if not data or 'sender_id' not in data or 'recipient_id' not in data or 'text' not in data:
        return {"error": "Missing fields"}, 400

    message_id = str(uuid.uuid4())

    query = f"""
        DECLARE $message_id AS Utf8;
        DECLARE $sender_id AS Utf8;
        DECLARE $recipient_id AS Utf8;
        DECLARE $text AS Utf8;

        INSERT INTO `{config.YDB_TABLE_PATH}` 
        (message_id, sender_id, recipient_id, text, created_at, status)
        VALUES ($message_id, $sender_id, $recipient_id, $text, CurrentUtcTimestamp(), "new");
    """

    # ✅ Правильная передача параметров с типами
    params = ydb.TypedParameters()
    params = params\
        .put('$message_id', ydb.PrimitiveTypeUtf8).with_value(message_id)\
        .put('$sender_id', ydb.PrimitiveTypeUtf8).with_value(str(data['sender_id']))\
        .put('$recipient_id', ydb.PrimitiveTypeUtf8).with_value(str(data['recipient_id']))\
        .put('$text', ydb.PrimitiveTypeUtf8).with_value(str(data['text']))\
        .end()

    try:
        ydb_client.execute(query, params)
        return {"message_id": message_id, "status": "queued"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
```

---

