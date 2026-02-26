### Запуск проекта через Docker Compose

Этот репозиторий содержит конфигурацию `docker-compose.yaml` для запуска учебного Django/DRF‑проекта с базой данных PostgreSQL, брокером Redis и очередями Celery (worker и Celery Beat).

#### 1. Подготовка окружения

- **Установите Docker и Docker Compose** согласно документации Docker для вашей ОС.
- **Склонируйте репозиторий** с проектом (эта домашняя работа должна быть оформлена отдельной веткой от `develop`).

#### 2. Настройка переменных окружения

1. В корне репозитория находится шаблон файла переменных окружения:
   - `.env.example`
2. Скопируйте его в файл `.env`:

```bash
Copy-Item .env.example .env
```

3. Отредактируйте `.env` при необходимости:
- **DJANGO_SECRET_KEY** — секретный ключ Django.
- **DJANGO_DEBUG** — режим отладки (`True`/`False`).
- **DJANGO_ALLOWED_HOSTS** — список хостов, через которые будет доступен бэкенд.
- **POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD** — настройки базы данных PostgreSQL.
- **REDIS_HOST / REDIS_PORT** — настройки Redis.
- **CELERY_BROKER_URL / CELERY_RESULT_BACKEND** — адреса брокера и хранилища результатов для Celery.

Файл `.env` **не должен попадать в репозиторий**.

#### 3. Запуск проекта

Находясь в корне репозитория (где лежит `docker-compose.yaml`), выполните:

```bash
docker compose up -d --build
```

- Флаг `--build` гарантирует пересборку образа бэкенда.
- Флаг `-d` запускает контейнеры в фоновом режиме.

Будут подняты следующие сервисы:
- **backend** — Django/DRF‑приложение.
- **db** — PostgreSQL.
- **redis** — Redis.
- **celery** — Celery worker.
- **celery-beat** — планировщик задач Celery Beat.

#### 4. Проверка работоспособности сервисов

- **Бэкенд (Django/DRF)**  
  Откройте в браузере:
  - `http://localhost:8000/`  
  или конкретный API‑эндпоинт проекта.  
  Также можно посмотреть логи:
  ```bash
  docker compose logs backend
  ```

- **PostgreSQL (db)**  
  Убедитесь, что контейнер в состоянии `Up`:
  ```bash
  docker compose ps db
  ```
  При необходимости можно подключиться к базе:
  ```bash
  docker compose exec db psql -U <POSTGRES_USER> -d <POSTGRES_DB> -c "\l"
  ```

- **Redis**  
  Проверка командой `PING`:
  ```bash
  docker compose exec redis redis-cli ping
  ```
  В ответ должно прийти `PONG`.

- **Celery worker**  
  Просмотр логов:
  ```bash
  docker compose logs celery
  ```
  В логах должны быть сообщения о подключении к брокеру и обработке задач.

- **Celery Beat**  
  Просмотр логов:
  ```bash
  docker compose logs celery-beat
  ```
  Должны быть видны периодические сообщения о запуске запланированных задач.

#### 5. Остановка и очистка

- **Остановить контейнеры, не удаляя данные:**

```bash
docker compose down
```

- **Остановить контейнеры и удалить связанные тома (например, данные БД):**

```bash
docker compose down -v
```

#### 6. Git и GitHub

- Все изменения (включая `docker-compose.yaml`, `.env.example`, `README.md` и `.gitignore`) должны быть закоммичены в ветке домашнего задания.
- Файл `.env` и другие игнорируемые файлы (виртуальное окружение, кэш и т. п.) **не должны попасть в коммиты**.
- Для сдачи домашнего задания создайте **pull request из ветки с домашкой в ветку `develop`** и отправьте ссылку наставнику.

