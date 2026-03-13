### 1. Запуск локально (Docker Compose)

Этот репозиторий содержит конфигурацию `docker-compose.yaml` для запуска учебного Django/DRF‑проекта с базой данных PostgreSQL, брокером Redis и очередями Celery (worker и Celery Beat).

#### 1.1. Подготовка окружения

- **Установите Docker и Docker Compose (docker compose)** согласно документации Docker для вашей ОС.
- **Склонируйте репозиторий** с проектом (домашняя работа — отдельная ветка от `develop`).

#### 1.2. Настройка переменных окружения

1. В корне репозитория находится шаблон файла переменных окружения:
   - `.env.example`
2. Скопируйте его в файл `.env` (PowerShell):

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
- **STRIPE_SECRET_KEY** — ключ Stripe (если используется).

Файл `.env` **не должен попадать в репозиторий**.

#### 1.3. Запуск проекта (Docker)

Находясь в корне репозитория (где лежит `docker-compose.yaml`), выполните:

```bash
docker compose up -d --build
```

- **`--build`** гарантирует пересборку образа бэкенда.
- **`-d`** запускает контейнеры в фоновом режиме.

Будут подняты следующие сервисы:
- **backend** — Django/DRF‑приложение.
- **db** — PostgreSQL.
- **redis** — Redis.
- **celery** — Celery worker.
- **celery-beat** — планировщик задач Celery Beat.

#### 1.4. Проверка работоспособности сервисов (Docker)

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

#### 1.5. Остановка и очистка (Docker)

- **Остановить контейнеры, не удаляя данные:**

```bash
docker compose down
```

- **Остановить контейнеры и удалить связанные тома (например, данные БД):**

```bash
docker compose down -v
```

### 2. Настройка удалённого сервера (ручной деплой без Docker)

- **ОС**: Ubuntu 22.04 LTS (рекомендуется).
- **Требования**:
  - Python 3.10+ и `venv`
  - Git
  - Nginx
  - systemd (для сервиса приложения)

#### 2.1. Базовая настройка сервера

- Обновите пакеты:
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```
- Установите зависимости:
  ```bash
  sudo apt install -y python3 python3-venv python3-pip git nginx
  ```
- Настройте SSH‑доступ **по ключу** (закрытый ключ потом добавляется как Secret `SSH_KEY` в GitHub)

#### 2.2. Файрвол (ufw)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

#### 2.3. Клонирование проекта на сервер

```bash
cd /var/www
sudo mkdir -p online_school
sudo chown "$USER":"$USER" online_school
cd online_school
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
```

Создайте `.env` на сервере на основе шаблона:

```bash
cp .env.example .env
nano .env
```

Заполните значения для прод‑окружения (секреты, БД, домен и т. д.).

#### 2.4. Виртуальное окружение и зависимости

```bash
cd /var/www/online_school
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Примените миграции и соберите статику:

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

#### 2.5. Gunicorn + systemd

Создайте сервис, например `online_school.service`:

```bash
sudo nano /etc/systemd/system/online_school.service
```

Пример содержимого:

```ini
[Unit]
Description=Online School Django app
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/online_school
Environment="DJANGO_SETTINGS_MODULE=config.settings"
ExecStart=/var/www/online_school/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Примените:

```bash
sudo systemctl daemon-reload
sudo systemctl enable online_school.service
sudo systemctl start online_school.service
sudo systemctl status online_school.service
```

#### 2.6. Nginx (reverse proxy)

Создайте конфиг:

```bash
sudo nano /etc/nginx/sites-available/online_school
```

Пример:

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активируйте сайт:

```bash
sudo ln -s /etc/nginx/sites-available/online_school /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Теперь приложение должно быть доступно по IP или домену.

### 3. GitHub Actions: CI/CD (тесты + деплой)

Файл workflow: `.github/workflows/ci-cd.yaml`.

#### 3.1. Что делает workflow

- **`lint` job**: запускает `flake8` (статический анализ кода).
- **`test` job** (после `lint`):
  - Устанавливает зависимости (`requirements.txt`).
  - Применяет миграции (SQLite в CI).
  - Запускает `python manage.py test`.
  - При ошибках тестов деплой **не выполняется**.
- **`deploy` job** (только для ветки `develop` и только после успешного `test`):
  - Подключается по SSH к удалённому серверу.
  - `rsync`‑ом заливает код в директорию деплоя.
  - На сервере разворачивает/обновляет `venv`, ставит зависимости, выполняет `migrate` и `collectstatic`.
  - Перезапускает systemd‑сервис (`online_school.service` или любой, который вы укажете в секретах).
- **`docker-build-and-push` job** (доп. задание):
  - Собирает Docker‑образ из `Dockerfile`.
  - Пушит образ в Docker Hub с тегами `latest` и `SHA`.

#### 3.2. Секреты GitHub (Settings → Secrets and variables → Actions)

Добавьте в репозиторий:

- **SSH/сервер**
  - `SERVER_IP` — IP‑адрес сервера.
  - `SSH_USER` — пользователь для SSH (обычно не `root`).
  - `SSH_KEY` — приватный SSH‑ключ (тот, что разрешён на сервере в `~/.ssh/authorized_keys`).
  - `DOCKER_CONTAINER_NAME` — имя контейнера на сервере, например `online-school`.

- **Docker (для доп. задания)**
  - `DOCKER_HUB_USERNAME` — ваш логин Docker Hub.
  - `DOCKER_HUB_ACCESS_TOKEN` — токен доступа Docker Hub.
  - `DOCKER_IMAGE_NAME` — имя репозитория образа, например `online-school`.

#### 3.3. Как запускается workflow

- Workflow автоматически запускается **при любом `push` в любую ветку**.
- Деплой выполняется **только** при `push` в ветку `develop` (`if: github.ref == 'refs/heads/develop'` в job `deploy` и `docker-build-and-push`).

### 4. Git и GitHub (для сдачи домашки)

- Все изменения (включая `.github/workflows/ci-cd.yaml`, `docker-compose.yaml`, `.env.example`, `README.md`, `.gitignore`, `Dockerfile`) должны быть закоммичены в ветке домашнего задания.
- Файл `.env` и другие игнорируемые файлы (виртуальное окружение, кэш и т. п.) **не должны попасть в коммиты**.
- Для сдачи домашнего задания создайте **pull request из ветки с домашкой в ветку `develop`** и отправьте ссылку наставнику.

