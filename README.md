# Course Catalog

Единый репозиторий приложения каталога курсов для деплоя через Coolify.

```text
frontend/  Next.js интерфейс
backend/   FastAPI и Alembic
database/  SQL-схема и начальные данные
deploy/    Nginx-шлюз для сайта и API
```

## Деплой

1. В Coolify подключите этот Git-репозиторий как **Docker Compose** с корневым файлом `docker-compose.yml`.
2. В режиме **Developer View** Coolify задайте переменные из `.env.example`. Установите длинный пароль в `POSTGRES_PASSWORD` и укажите тот же пароль в `DATABASE_URL`. Файл `.env` не добавляйте в Git.
3. В разделе **Domains** назначьте `https://course-catalog-final.salli95.win` сервису `gateway` на внутренний порт `80`.
4. Разверните приложение. Домен открывает фронтенд, запросы `/api/...` проходят через шлюз к FastAPI.

Cloudflare Tunnel должен направлять этот hostname на `https://localhost:443` с HTTP Host Header `course-catalog-final.salli95.win`, как настроено для домена.

PostgreSQL сохраняет данные в volume `postgres_data`. `schema.sql` и `seed.sql` запускаются только при первом создании пустого volume; повторный деплой существующие данные не пересоздаёт.

Для локального запуска скопируйте `.env.example` в `.env`, задайте пароль и выполните `docker compose up -d --build`.
