# План разработки фронтенда на .NET MAUI

## Стек технологий
- **.NET MAUI** – кросс-платформенный UI (Android, iOS, Windows, macOS).
- **CommunityToolkit.MVVM** – архитектурный паттерн MVVM.
- **SQLite-net-pcl** – локальное хранение истории чатов.
- **HttpClient** – REST-взаимодействие с API Gateway.
- **Newtonsoft.Json / System.Text.Json** – работа с JSON.
- **SignalR** (перспектива) – real-time уведомления (пока polling).
- **Пуш-уведомления** – Firebase (Android), APNs (iOS) на будущее.

## Архитектура приложения
- **Модели (Models)**: Message, Conversation, User, ReceiptHandle и т.д.
- **Сервисы (Services)**:
  - `ApiService` (HttpClient) – методы `SendMessage`, `PollMessages`, `Acknowledge`.
  - `LocalDbService` – CRUD операций с SQLite: сохранить/получить сообщения, диалоги.
  - `SyncService` – фоновый polling (таймер или PeriodicTimer).
- **ViewModel** – бизнес-логика экранов, связь с сервисами через DI.
- **Views** – XAML-страницы.

## Этапы разработки

### Этап 1: Инфраструктура проекта
- Создать MAUI-проект, настроить DI (Microsoft.Extensions.DependencyInjection).
- Подключить NuGet-пакеты: `sqlite-net-pcl`, `CommunityToolkit.Mvvm`, `CommunityToolkit.Maui`.
- Реализовать `ApiService` на основе `HttpClient`, прописать base URL API Gateway.
- Реализовать простые DTO-классы.

### Этап 2: Локальное хранилище
- Спроектировать таблицы:
  - `Message` (Id, MessageId, SenderId, RecipientId, Text, CreatedAt, Status).
  - `Conversation` (Id, ParticipantId, LastMessage, UpdatedAt).
- Создать `DatabaseContext`, методы инициализации, миграции.
- `LocalDbService`: вставка/получение сообщений, обновление диалогов.

### Этап 3: Синхронизация сообщений (Polling)
- `SyncService` с таймером (интервал 5–10 сек) вызывает `PollMessages(recipientId)`.
- При получении новых сообщений:
  - Сохранить в локальную БД, избегая дубликатов (уникальный индекс по `MessageId`).
  - Отправить `Acknowledge` с `receipt_handles`.
  - Уведомить ViewModel через события (MessagingCenter / WeakReferenceMessenger) или `IObservable`.
- Фоновый процесс должен работать, пока приложение активно. При сворачивании – приостанавливать.

### Этап 4: Интерфейс списка диалогов
- `ConversationsPage` + `ConversationsViewModel`.
- Загрузка диалогов из локальной БД, отображение последнего сообщения.
- При получении нового сообщения – обновление диалога.
- Переход к чату.

### Этап 5: Чат-экран
- `ChatPage` + `ChatViewModel`.
- `CollectionView` для списка сообщений (свой шаблон).
- Поле ввода и кнопка отправки.
- При отправке:
  - Проверить, что текст не пуст.
  - Вызвать `ApiService.SendMessage(...)`.
  - При успехе – добавить сообщение в локальную БД и обновить UI.
  - При ошибке – пометить как `failed`, повторить позже.
- Входящие сообщения подгружаются через `SyncService`, автоматически появляются в списке (наблюдаемая коллекция).

### Этап 6: Доработка UX
- Индикация статуса сообщения (отправлено/доставлено/прочитано – в будущем).
- Pull-to-refresh в списке диалогов.
- Обработка сетевых ошибок, показ уведомлений.

### Этап 7: Аутентификация и безопасность
- Пока тестовые `user_id` берутся из настроек или статически.
- В дальнейшем внедрить OAuth2 (Yandex ID) или другой провайдер.
- Безопасное хранение токенов в SecureStorage.

### Этап 8: Real-time (на будущее)
- Заменить polling на WebSocket или SignalR (если API Gateway будет поддерживать).
- Оптимизировать потребление трафика и батареи.

## Целевая платформа
- Первоначально Android, затем iOS/Windows по мере готовности UI.

## Инструменты
- Visual Studio 2022+ с MAUI workload.
- Эмулятор Android / физическое устройство для отладки.
- Postman или аналоги для ручного тестирования API (уже есть `test.py`).

## Текущий статус бэкенда
Бэкенд стабилен, все тесты `test.py` проходят. API готов к интеграции.