# 📚 c0r.AI Documentation

Добро пожаловать в документацию проекта c0r.AI - системы анализа питания с использованием ИИ.

## 🚀 Быстрый старт

Если вы новичок в проекте, начните с этого раздела:

- **[Установка и настройка](getting-started/installation.md)** - Настройка окружения разработки
- **[Быстрый старт](getting-started/quick-start.md)** - Запуск проекта за 5 минут
- **[Получение Telegram ID](getting-started/GET_TELEGRAM_ID.md)** - Настройка Telegram интеграции
- **[Многоязычная поддержка](getting-started/multilingual-support.md)** - Интернационализация

## 🛠️ Разработка

Документация для разработчиков:

- **[Руководство контрибьютора](development/contributing.md)** - Как участвовать в разработке
- **[Архитектура системы](development/architecture.md)** - Обзор модульной архитектуры
- **[Руководство по тестированию](development/testing-guide.md)** - Написание и запуск тестов
- **[Защита от ошибок](development/error-protection.md)** - Обработка ошибок в системе
- **[Настройка GitHub Secrets](development/GITHUB_SECRETS_SETUP.md)** - Конфигурация CI/CD секретов
- **[Откат миграций](development/migration-rollback.md)** - Управление миграциями БД

## 🚀 Деплоймент

Развертывание в продакшн:

- **[Продакшн деплоймент](deployment/production-deployment.md)** - Основное руководство по развертыванию
- **[Деплоймент с тестами](deployment/deployment-with-tests.md)** - Развертывание с автотестами
- **[Безопасный деплоймент](deployment/safe-deployment.md)** - Стратегии безопасного развертывания
- **[Docker тестирование](deployment/docker-testing.md)** - Локальное тестирование с Docker
- **[NGINX SSL настройка](deployment/nginx-ssl-setup.md)** - Настройка веб-сервера

## 🧪 Тестирование

Руководства по тестированию:

- **[Продакшн тестирование](testing/production-testing.md)** - Тестирование в продакшн среде
- **[Команды тестирования](testing/production-commands.md)** - Полезные команды для тестов
- **[Быстрые тесты](testing/quick-tests.md)** - Экспресс-проверки системы
- **[Тестирование платежей](testing/payment-testing.md)** - Проверка платежных интеграций

## 🔌 Интеграции

Настройка внешних сервисов:

### Telegram
- **[Настройка платежей Telegram](integrations/TELEGRAM_PAYMENTS_SETUP.md)** - Интеграция платежей в боте
- **[Сценарии тестирования](integrations/TELEGRAM_TEST_SCENARIOS.md)** - Тестовые сценарии для бота

### Платежные системы
- **[Настройка YooKassa](integrations/YOOKASSA_SETUP.md)** - Подключение YooKassa
- **[YooKassa Webhooks](integrations/YOOKASSA_WEBHOOK_SETUP.md)** - Настройка вебхуков
- **[Получение ключей YooKassa](integrations/get_yookassa_keys.md)** - Управление API ключами

### Полная документация интеграций
- **[Все интеграции](integrations/)** - Полный список интеграций с внешними сервисами

## 💼 Бизнес документация

Бизнес-логика и планирование:

- **[Региональное предложение](business/regional-proposal.md)** - Предложение по региональной идентификации
- **[ChatGPT промпты](business/prompts_chatgpt/)** - Коллекция бизнес-промптов

## 📦 Архив

Историческая документация:

- **[Релизы](archive/releases/)** - Документация по версиям
- **[История миграций](archive/migration-history/)** - Журнал рефакторинга

## 🔍 Поиск по документации

### По категориям:
- **Новичкам**: [Быстрый старт](#-быстрый-старт)
- **Разработчикам**: [Разработка](#️-разработка)
- **DevOps**: [Деплоймент](#-деплоймент) + [Тестирование](#-тестирование)
- **Интеграторам**: [Интеграции](#-интеграции)
- **Менеджерам**: [Бизнес документация](#-бизнес-документация)

### По технологиям:
- **Python**: [Архитектура](development/architecture.md), [Тестирование](development/testing-guide.md)
- **Docker**: [Docker тестирование](deployment/docker-testing.md)
- **NGINX**: [NGINX SSL](deployment/nginx-ssl-setup.md)
- **Telegram**: [Telegram интеграции](integrations/telegram/)
- **Платежи**: [Платежные системы](integrations/payments/)

## 📞 Поддержка

Если вы не нашли ответ в документации:

1. Проверьте [Issues на GitHub](https://github.com/your-repo/issues)
2. Обратитесь к [руководству контрибьютора](development/contributing.md)
3. Создайте новый Issue с тегом `documentation`

---

**Последнее обновление**: 2025-01-21  
**Версия документации**: 2.2  
**Статус**: Активная разработка