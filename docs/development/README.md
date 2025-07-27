# 🛠️ Разработка

Документация для разработчиков c0r.AI системы.

## 📚 Руководства в этом разделе

### 1. [Руководство контрибьютора](contributing.md)
Как участвовать в разработке проекта:
- Процесс разработки
- Стандарты кодирования
- Pull Request workflow
- Code review процесс

### 2. [Архитектура системы](architecture.md)
Обзор модульной архитектуры:
- Структура сервисов
- Взаимодействие компонентов
- Паттерны проектирования
- Принципы организации кода

### 3. [Руководство по тестированию](testing-guide.md)
Написание и запуск тестов:
- Unit тесты
- Integration тесты
- Тестирование API
- Покрытие кода

### 4. [Защита от ошибок](error-protection.md)
Обработка ошибок в системе:
- Стратегии обработки ошибок
- Логирование
- Мониторинг
- Восстановление после сбоев

### 5. [Настройка GitHub Secrets](GITHUB_SECRETS_SETUP.md)
Конфигурация секретов для CI/CD:
- Настройка GitHub Actions
- Управление секретами
- Безопасность в CI/CD
- Автоматизация деплоймента

### 6. [Откат миграций](migration-rollback.md)
Управление миграциями базы данных:
- Создание миграций
- Применение изменений
- Откат изменений
- Безопасные практики

## 🎯 Для разных ролей

### Новые разработчики
1. Начните с [руководства контрибьютора](contributing.md)
2. Изучите [архитектуру системы](architecture.md)
3. Настройте [тестирование](testing-guide.md)

### Опытные разработчики
1. Изучите [архитектуру](architecture.md) для понимания принципов
2. Ознакомьтесь с [защитой от ошибок](error-protection.md)
3. Изучите процессы [миграций](migration-rollback.md)

### DevOps инженеры
1. [Архитектура системы](architecture.md) - для понимания компонентов
2. [Защита от ошибок](error-protection.md) - для мониторинга
3. [Миграции](migration-rollback.md) - для управления БД

## 🔧 Технологический стек

### Backend
- **Python 3.10+** - Основной язык
- **FastAPI** - API framework
- **Supabase** - База данных и аутентификация
- **OpenAI API** - Анализ изображений

### Frontend/Bot
- **python-telegram-bot** - Telegram интеграция
- **TypeScript** - Cloudflare Workers
- **Hono** - Edge API framework

### DevOps
- **Docker** - Контейнеризация
- **GitHub Actions** - CI/CD
- **NGINX** - Reverse proxy
- **Cloudflare** - CDN и Workers

## 📋 Процесс разработки

### 1. Планирование
- Создание Issue
- Обсуждение архитектуры
- Планирование тестов

### 2. Разработка
- Feature branch
- Следование стандартам кода
- Написание тестов

### 3. Тестирование
- Unit тесты
- Integration тесты
- Manual testing

### 4. Review
- Code review
- Архитектурный review
- Тестирование reviewer'ом

### 5. Деплоймент
- Merge в main
- Автоматический деплоймент
- Мониторинг

## 🚀 Быстрые ссылки

### Настройка окружения
- [Установка](../getting-started/installation.md)
- [Быстрый старт](../getting-started/quick-start.md)

### Тестирование
- [Локальное тестирование](testing-guide.md)
- [Продакшн тесты](../testing/)

### Деплоймент
- [Продакшн деплоймент](../deployment/production-deployment.md)
- [Docker setup](../deployment/docker-testing.md)

## 📞 Поддержка разработчиков

### Внутренние ресурсы
- **Slack/Discord** - Ежедневное общение
- **GitHub Discussions** - Архитектурные вопросы
- **Issues** - Баги и feature requests

### Внешние ресурсы
- **Python docs** - python.org
- **FastAPI docs** - fastapi.tiangolo.com
- **Supabase docs** - supabase.com/docs
- **OpenAI docs** - platform.openai.com/docs

---

**Последнее обновление**: 2025-01-21  
**Мейнтейнеры**: Development Team  
**Статус**: Активная разработка