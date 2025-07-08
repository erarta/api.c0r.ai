# c0r.ai Monorepo

## Структура

- `/api.c0r.ai/` — публичный API и Telegram-бот (Python, FastAPI)
- `/ml.c0r.ai/` — ML-инференс сервис (Python, FastAPI, проксирует OpenAI/Gemini)
- `/pay.c0r.ai/` — платёжный сервис (Python, FastAPI, модульная архитектура, YooKassa)
- `/common/` — общие утилиты, схемы, константы
- `/scripts/` — миграции, деплой, вспомогательные скрипты

## Быстрый старт (локально)

```bash
git clone https://github.com/erarta/api.c0r.ai.git
cd api.c0r.ai
cp .env.example .env
docker-compose up --build
```

## Переменные окружения

См. `.env.example` — все ключи и токены для сервисов.

## Деплой на AWS EC2

1. Установите Docker и docker-compose на сервере.
2. Клонируйте репозиторий и настройте `.env`.
3. Запустите сервисы:
   ```bash
   docker-compose up --build -d
   ```
4. Настройте DNS для поддоменов (`api.c0r.ai`, `ml.c0r.ai`, `pay.c0r.ai`) на IP вашего EC2.
5. Установите nginx и настройте reverse proxy (см. `nginx.conf.example`).
6. Настройте HTTPS через certbot:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx
   ```

## Пример nginx.conf

См. `nginx.conf.example` в корне репозитория.

## Сервисы

- **api.c0r.ai** — Telegram-бот, публичный API, проверка подписки, проксирование к ML
- **ml.c0r.ai** — ML-инференс (OpenAI/Gemini, в будущем — своя модель)
- **pay.c0r.ai** — генерация инвойсов YooKassa, обработка webhook
- **common/** — общие схемы, утилиты

---

## Контакты и поддержка

[erarta/api.c0r.ai](https://github.com/erarta/api.c0r.ai) 