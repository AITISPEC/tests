# Dump: deploy

**Root:** `C:\Users\AITISPEC\PycharmProjects\klaim\deploy`

---

## 📄 ack.py

```py
# handlers/ack.py
from ydb_client import ydb_client
import ydb
import uuid
from config import Config
import json

config = Config()

def ack(data):
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

## 📄 config.py

```py
import os


class Config:
    YDB_ENDPOINT = os.getenv("YDB_ENDPOINT")
    YDB_DATABASE = os.getenv("YDB_DATABASE")
    YDB_TABLE_NAME = os.getenv("YDB_TABLE_NAME")
```

---

## 📄 index.py

```py
import ydb
import os
import json
from config import Config

config = Config()
my_table = config.YDB_TABLE_NAME

driver = ydb.Driver(
    endpoint=os.getenv('YDB_ENDPOINT'),
    database=os.getenv('YDB_DATABASE'),
    credentials=ydb.iam.MetadataUrlCredentials(),
)

driver.wait(fail_fast=True, timeout=5)
pool = ydb.SessionPool(driver)

def execute_query(session, recipient_id, message_id, sender_id):
    query = f'''
        UPSERT INTO {my_table}
        (recipient_id, message_id, sender_id)
        VALUES (@recipient_id, @message_id, @sender_id);
    '''
    params = {
        'recipient_id': recipient_id,
        'message_id': message_id,
        'sender_id': sender_id
    }
    return session.transaction().execute(
        query,
        params,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    )

def handler(event, context):
    try:
        # Безопасное извлечение body из event
        if event is None:
            return {
                'statusCode': 400,
                'body': 'Event is None'
            }

        if not isinstance(event, dict):
            return {
                'statusCode': 400,
                'body': f'Event must be a dict, got {type(event)}'
            }

        raw_body = event.get('body')
        if raw_body is None:
            body_data = {}
        else:
            if isinstance(raw_body, str):
                try:
                    body_data = json.loads(raw_body)
                except json.JSONDecodeError:
                    return {
                        'statusCode': 400,
                        'body': 'Invalid JSON in body'
                    }
            else:
                body_data = raw_body

        # Извлекаем параметры
        recipient_id = body_data.get('recipient_id')
        message_id = body_data.get('message_id')
        sender_id = body_data.get('sender_id')

        # Проверка обязательных полей
        missing_fields = []
        if recipient_id is None:
            missing_fields.append('recipient_id')
        if message_id is None:
            missing_fields.append('message_id')
        if sender_id is None:
            missing_fields.append('sender_id')

        if missing_fields:
            return {
                'statusCode': 400,
                'body': f'Missing required parameters: {", ".join(missing_fields)}'
            }

        # Выполняем UPSERT
        result = pool.retry_operation_sync(
            lambda session: execute_query(session, recipient_id, message_id, sender_id)
        )

        # Детальная проверка результата
        if not result or len(result) == 0:
            return {
                'statusCode': 500,
                'body': 'Query completed but returned empty result set'
            }
        else:
            return {
                'statusCode': 200,
                'body': 'Data upserted successfully'
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }
```

---

## 📄 poll.py

```py
# handlers/poll.py
from ydb_client import ydb_client
import ydb
import uuid
from config import Config
import json

config = Config()


def poll(recipient_id, last_id=None):
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

## 📄 requirements.txt

```txt
ydb==3.26.6
```

---

## 📄 send.py

```py
# handlers/send.py
from ydb_client import ydb_client
import ydb
import uuid
from config import Config


config = Config()

def send(data):
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

## 📄 ydb_client.py

```py
# ydb_client.py
import os
import ydb
import ydb.iam


class YDBClient:
    def __init__():
        endpoint = os.getenv('YDB_ENDPOINT')
        database = os.getenv('YDB_DATABASE')
        credentials = ydb.iam.MetadataUrlCredentials()

        driver_config = ydb.DriverConfig(
            endpoint=endpoint,
            database=database,
            credentials=credentials
        )
        driver = ydb.Driver(driver_config)
        driver.wait(fail_fast=True, timeout=10)
        print("YDB Client Initialized")
        return ydb.SessionPool(driver)

    def execute(self, query, params=None):
        def _execute_query(session):
            return session.transaction().execute(
                query,
                parameters=params,
                commit_tx=True
            )
        return self.pool.retry_operation_sync(_execute_query)


ydb_client = YDBClient()
```

---

