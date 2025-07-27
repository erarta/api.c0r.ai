# Анализ текущей структуры проекта c0r.ai

*Дата создания: 27 января 2025*
*Цель: Документирование базовой структуры для ребрендинга в AIDI.APP*

## 📁 Полная структура проекта

```
c0r.ai/
├── CHANGELOG.md                    # История изменений
├── docker-compose.yml              # Оркестрация сервисов
├── LICENSE.md                      # Лицензия
├── nginx.conf.example              # Конфигурация nginx
├── nginx.conf.production           # Продакшн конфигурация nginx
├── package.json                    # Node.js зависимости (для Edge API)
├── README.md                       # Основная документация
├── requirements.txt                # Python зависимости
├── start_services.sh               # Скрипт запуска сервисов
├── stop_services.sh                # Скрипт остановки сервисов
├── test_services.py                # Тестирование сервисов
│
├── assets/                         # Статические ресурсы
│
├── c0r/                           # Python виртуальное окружение
│   ├── bin/
│   ├── include/
│   └── lib/python3.13/site-packages/
│
├── changelogs/                     # Детальные логи изменений
│   └── CURRENT.md
│
├── common/                         # Общие компоненты
│   ├── database/                   # Модели базы данных
│   ├── config/                     # Конфигурационные файлы
│   └── utils/                      # Утилиты
│
├── docs/                          # Документация
│   ├── api/                       # API документация
│   ├── deployment/                # Документация по развертыванию
│   ├── development/               # Документация для разработчиков
│   ├── guides/                    # Руководства пользователя
│   ├── integrations/              # Интеграции с внешними сервисами
│   └── testing/                   # Документация по тестированию
│
├── i18n/                          # Интернационализация
│   ├── en/                        # Английские переводы
│   │   ├── welcome.py
│   │   ├── help.py
│   │   ├── profile.py
│   │   ├── payments.py
│   │   ├── errors.py
│   │   ├── nutrition.py
│   │   ├── daily.py
│   │   ├── recipes.py
│   │   └── reports.py
│   └── ru/                        # Русские переводы (зеркальная структура)
│
├── migrations/                     # Миграции базы данных
│   ├── README.md
│   └── [YYYY-MM-DD]_*.sql
│
├── rebranding/                     # Предыдущие планы ребрендинга
├── rebranding_claude/              # Планы ребрендинга Claude
│
├── scripts/                        # Скрипты автоматизации
│   ├── run_migrations.py
│   └── deployment/
│
├── services/                       # Микросервисы (ОСНОВНАЯ АРХИТЕКТУРА)
│   ├── README.md
│   │
│   ├── api/                       # API Service (Port 8000)
│   │   ├── README.md
│   │   ├── bot/                   # Telegram Bot
│   │   │   ├── bot.py             # Основной файл бота
│   │   │   ├── config.py          # Конфигурация бота
│   │   │   ├── main.py            # Точка входа
│   │   │   ├── Dockerfile         # Docker контейнер
│   │   │   ├── requirements.txt   # Python зависимости
│   │   │   ├── handlers/          # Обработчики команд
│   │   │   │   ├── __init__.py
│   │   │   │   ├── commands.py    # Базовые команды
│   │   │   │   ├── daily.py       # Ежедневная статистика
│   │   │   │   ├── keyboards.py   # Клавиатуры
│   │   │   │   ├── language.py    # Переключение языка
│   │   │   │   ├── nutrition.py   # Анализ питания
│   │   │   │   ├── payments.py    # Платежи
│   │   │   │   ├── photo.py       # Обработка фото
│   │   │   │   ├── profile.py     # Профиль пользователя
│   │   │   │   └── recipe.py      # Генерация рецептов
│   │   │   └── utils/             # Утилиты бота
│   │   │       ├── __init__.py
│   │   │       ├── r2.py          # Cloudflare R2 интеграция
│   │   │       └── supabase.py    # Supabase интеграция
│   │   │
│   │   ├── edge/                  # Edge API (Cloudflare Workers)
│   │   │   ├── worker.ts          # Основной worker
│   │   │   ├── tsconfig.json      # TypeScript конфигурация
│   │   │   └── lib/               # Библиотеки
│   │   │       ├── openai.ts      # OpenAI интеграция
│   │   │       ├── r2.ts          # R2 интеграция
│   │   │       └── supabase.ts    # Supabase интеграция
│   │   │
│   │   └── shared/                # Общие компоненты API
│   │
│   ├── ml/                        # ML Service (Port 8001)
│   │   ├── README.md
│   │   ├── main.py                # FastAPI приложение
│   │   ├── Dockerfile             # Docker контейнер
│   │   ├── requirements.txt       # Python зависимости
│   │   ├── gemini/                # Gemini AI интеграция
│   │   │   └── client.py
│   │   ├── openai/                # OpenAI интеграция
│   │   │   └── client.py
│   │   └── shared/                # Общие ML компоненты
│   │
│   └── pay/                       # Payment Service (Port 8002)
│       ├── README.md
│       ├── __init__.py
│       ├── config.py              # Конфигурация платежей
│       ├── main.py                # FastAPI приложение
│       ├── Dockerfile             # Docker контейнер
│       ├── requirements.txt       # Python зависимости
│       ├── shared/                # Общие компоненты платежей
│       ├── stripe/                # Stripe интеграция
│       │   ├── __init__.py
│       │   ├── client.py          # Stripe клиент
│       │   ├── config.py          # Stripe конфигурация
│       │   ├── README.md
│       │   └── webhooks.py        # Stripe webhooks
│       ├── yookassa/              # YooKassa интеграция
│       │   ├── __init__.py
│       │   ├── client.py          # YooKassa клиент
│       │   ├── config.py          # YooKassa конфигурация
│       │   └── README.md
│       ├── yookassa_handlers/     # YooKassa обработчики
│       │   ├── __init__.py
│       │   ├── client.py
│       │   └── config.py
│       └── templates/             # HTML шаблоны
│           └── payment_success.html
│
├── shared/                        # Общие контракты между сервисами
│   ├── contracts/                 # Контракты API между сервисами
│   │   ├── api_ml.py             # API ↔ ML коммуникация
│   │   ├── api_pay.py            # API ↔ Payment коммуникация
│   │   └── ml_pay.py             # ML ↔ Payment коммуникация
│   └── utils/                     # Общие утилиты
│
├── supabase/                      # Supabase конфигурация
│   ├── config.toml
│   └── migrations/
│
└── tests/                         # Тесты
    ├── unit/                      # Юнит тесты
    ├── integration/               # Интеграционные тесты
    ├── e2e/                       # End-to-end тесты
    ├── fixtures/                  # Тестовые данные
    └── conftest.py               # Pytest конфигурация
```

## 🏗️ Архитектура сервисов

### ✅ Правильное разделение сервисов (уже реализовано)

**API Service (Port 8000):**
- Telegram bot handlers и клавиатуры
- FastAPI endpoints
- Аутентификация пользователей и middleware
- FSM управление состояниями
- Маршрутизация запросов к ML и Payment сервисам

**ML Service (Port 8001):**
- Gemini AI интеграция для анализа питания
- OpenAI интеграция для генерации рецептов
- Обработка и анализ изображений
- Управление AI моделями

**Payment Service (Port 8002):**
- Stripe интеграция для международных платежей
- YooKassa интеграция для российских платежей
- Обработка webhooks
- Валидация и обработка платежей

### Паттерн коммуникации
Сервисы взаимодействуют через HTTP API вызовы, используя общие контракты:
- `shared/contracts/api_ml.py` - API ↔ ML коммуникация
- `shared/contracts/api_pay.py` - API ↔ Payment коммуникация
- `shared/contracts/ml_pay.py` - ML ↔ Payment коммуникация

## 🗄️ Текущая схема базы данных

### Основные таблицы (для анализа питания)
- **users** - пользователи системы
- **user_profiles** - профили пользователей с настройками питания
- **nutrition_analyses** - результаты анализа питания
- **recipes** - сгенерированные рецепты
- **daily_stats** - ежедневная статистика
- **payments** - история платежей
- **credits** - система кредитов
- **schema_migrations** - отслеживание миграций

## 🌐 Интернационализация

### Текущая структура i18n
- **Поддерживаемые языки:** English (en), Russian (ru)
- **Модули переводов:**
  - `welcome.py` - приветственные сообщения
  - `help.py` - справочная информация
  - `profile.py` - управление профилем
  - `payments.py` - платежные сообщения
  - `errors.py` - сообщения об ошибках
  - `nutrition.py` - анализ питания
  - `daily.py` - ежедневная статистика
  - `recipes.py` - генерация рецептов
  - `reports.py` - отчеты

## 💳 Система платежей

### Текущие интеграции
- **Stripe** - международные платежи (USD, EUR)
- **YooKassa** - российские платежи (RUB)
- **Кредитная система** - внутренняя валюта для оплаты услуг

### Поддерживаемые методы
- Банковские карты
- Электронные кошельки
- Telegram Payments (через YooKassa)

## 🔧 Инфраструктура

### Развертывание
- **Docker Compose** - локальная разработка
- **Nginx** - reverse proxy и load balancing
- **Supabase** - PostgreSQL база данных
- **Cloudflare R2** - хранение файлов
- **AWS EC2** - хостинг сервисов

### Мониторинг и логирование
- Структурированное логирование
- Health check endpoints
- Метрики производительности

## 📊 Текущие FSM состояния

### Состояния бота (для питания)
1. **Default** - основное меню
2. **Nutrition Analysis** - анализ питания по фото
3. **Recipe Generation** - генерация рецептов

## 🔄 Что нужно адаптировать для AIDI.APP

### Сохранить (готовая архитектура)
- ✅ Разделение на микросервисы
- ✅ Система платежей (Stripe + YooKassa)
- ✅ Интернационализация (i18n)
- ✅ Система миграций БД
- ✅ Docker контейнеризация
- ✅ Общие контракты между сервисами
- ✅ Система тестирования

### Адаптировать
- 🔄 FSM состояния (default → reputation → deepfake)
- 🔄 Обработчики команд (nutrition → reputation/kyc)
- 🔄 ML интеграции (питание → репутация/дипфейки)
- 🔄 Схема базы данных (питание → репутация/kyc)
- 🔄 i18n переводы (питание → кибербезопасность)
- 🔄 Домены (c0r.ai → aidi.app)

### Добавить новое
- ➕ Интеграция с источниками данных для репутации
- ➕ Алгоритмы детекции дипфейков
- ➕ KYC верификация документов
- ➕ Система скоринга репутации
- ➕ API для внешних интеграций

## 🎯 Выводы

Текущая архитектура c0r.ai отлично подходит для ребрендинга в AIDI.APP:

1. **Микросервисная архитектура** уже правильно реализована
2. **Система платежей** готова для новых тарифов
3. **Интернационализация** легко адаптируется
4. **Инфраструктура** масштабируема для новых функций
5. **Codebase** хорошо структурирован и документирован

Основная работа будет заключаться в адаптации бизнес-логики, а не в переписывании архитектуры.