# ⚡ Быстрый старт

Запустите c0r.AI за 5 минут! Это руководство поможет вам быстро проверить основную функциональность.

## 🎯 Цель

Быстро запустить систему и протестировать основные компоненты:
- Telegram Bot
- API анализа питания
- Платежная система (тестовый режим)

## ⚡ Экспресс-настройка

### 1. Клонирование и установка

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd api.c0r.ai

# Установите зависимости
pip install -r requirements.txt
npm install
```

### 2. Минимальная конфигурация

Создайте `.env` файл с минимальными настройками:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_SERVICE_BOT_TOKEN=your_service_bot_token_here

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_key

# OpenAI
OPENAI_API_KEY=your_openai_key

# Тестовые платежи
YOOKASSA_SHOP_ID=test_shop_id
YOOKASSA_SECRET_KEY=test_secret_key
```

### 3. Быстрый запуск

```bash
# Запуск Telegram бота
cd services/api/bot
python main.py

# В другом терминале - запуск Edge API (если нужно)
cd services/api/edge
npm run dev
```

## 🧪 Быстрая проверка

### Тест 1: Telegram Bot
1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Загрузите фото еды
4. Получите анализ питания

### Тест 2: API Endpoint
```bash
curl -X POST http://localhost:8787/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_url": "test_image_url"}'
```

### Тест 3: Платежи (тестовый режим)
1. В боте выберите "Купить кредиты"
2. Выберите тестовый план
3. Проведите тестовый платеж

## 🔍 Проверка компонентов

### Проверка базы данных
```bash
# Проверка подключения к Supabase
python -c "
from common.db.supabase_client import get_supabase_client
client = get_supabase_client()
print('✅ Supabase подключен')
"
```

### Проверка OpenAI
```bash
# Тест OpenAI API
python -c "
from services.ml.openai.client import OpenAIClient
client = OpenAIClient()
print('✅ OpenAI подключен')
"
```

### Проверка платежей
```bash
# Тест YooKassa
python -c "
from services.pay.yookassa.client import YooKassaClient
client = YooKassaClient()
print('✅ YooKassa подключен')
"
```

## 🚨 Частые проблемы

### Проблема: Bot не отвечает
**Решение:**
```bash
# Проверьте токен
echo $TELEGRAM_BOT_TOKEN

# Проверьте логи
tail -f logs/bot.log
```

### Проблема: Ошибка анализа изображений
**Решение:**
```bash
# Проверьте OpenAI ключ
python -c "import openai; print(openai.api_key[:10] + '...')"

# Проверьте лимиты API
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/usage
```

### Проблема: Ошибки базы данных
**Решение:**
```bash
# Проверьте подключение к Supabase
python -c "
from supabase import create_client
client = create_client('$SUPABASE_URL', '$SUPABASE_SERVICE_ROLE_KEY')
print('✅ Подключение работает')
"
```

## 📊 Мониторинг

### Основные логи
```bash
# Логи бота
tail -f services/api/bot/logs/app.log

# Логи платежей
tail -f services/pay/logs/payments.log

# Системные логи
tail -f logs/system.log
```

### Проверка статуса
```bash
# Проверка всех сервисов
python scripts/health_check.py

# Быстрая проверка
curl http://localhost:8787/health
```

## 🎯 Что дальше?

После успешного быстрого старта:

1. **Полная настройка**: [Детальная установка](installation.md)
2. **Разработка**: [Архитектура системы](../development/architecture.md)
3. **Тестирование**: [Руководство по тестированию](../development/testing-guide.md)
4. **Деплоймент**: [Продакшн развертывание](../deployment/production-deployment.md)

## 💡 Полезные команды

```bash
# Перезапуск всех сервисов
./scripts/restart_all.sh

# Очистка логов
./scripts/clear_logs.sh

# Проверка конфигурации
python scripts/validate_config.py

# Бэкап базы данных
./scripts/backup_db.sh
```

## 🆘 Нужна помощь?

- **Детальная настройка**: [installation.md](installation.md)
- **Проблемы с интеграциями**: [../integrations/](../integrations/)
- **Ошибки в продакшн**: [../deployment/](../deployment/)
- **GitHub Issues**: Создайте issue с тегом `quick-start`

---

**Время выполнения**: ~5 минут  
**Сложность**: Начинающий  
**Требования**: Python 3.10+, Node.js 16+