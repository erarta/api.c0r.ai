# 🚀 Руководство по тестированию c0r.ai на продакшене

## 📋 Предварительные требования

### Перед деплоем убедитесь:
- [ ] Все сервисы собираются без ошибок
- [ ] YooKassa API ключи получены из личного кабинета
- [ ] Telegram Bot настроен в BotFather
- [ ] SSL сертификаты настроены для всех поддоменов
- [ ] Supabase база данных готова

## 🔧 Подготовка к деплою

### 1. Обновите production environment
```bash
# Скопируйте production конфиг
cp .env.production.example .env.production

# Обновите переменные:
YOOKASSA_SHOP_ID=ваш_реальный_shop_id
YOOKASSA_SECRET_KEY=ваш_реальный_secret_key
YOOKASSA_PROVIDER_TOKEN=ваш_provider_token_из_botfather
```

### 2. Проверьте сервисы перед деплоем
```bash
# Соберите все сервисы
docker-compose build

# Запустите локально для финальной проверки
docker-compose up -d

# Проверьте статус
docker-compose ps
```

## 🚀 Процедура деплоя

### 1. Деплой на AWS EC2
```bash
# Подключитесь к серверу
ssh -i your-key.pem ubuntu@your-server-ip

# Клонируйте репозиторий
git clone https://github.com/your-username/api.c0r.ai.git
cd api.c0r.ai

# Запустите setup скрипт
chmod +x scripts/setup-production.sh
./scripts/setup-production.sh

# Переключитесь на production environment
chmod +x scripts/switch-env.sh
./scripts/switch-env.sh production
```

### 2. Настройка SSL и Nginx
```bash
# Получите SSL сертификаты
sudo certbot --nginx -d api.c0r.ai -d ml.c0r.ai -d pay.c0r.ai

# Скопируйте production nginx конфиг
sudo cp nginx.conf.production /etc/nginx/sites-available/c0r.ai
sudo ln -s /etc/nginx/sites-available/c0r.ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Запуск сервисов
```bash
# Запустите все сервисы
docker-compose -f docker-compose.yml up -d

# Проверьте статус
docker-compose ps
docker-compose logs -f
```

## 🧪 Тестирование на продакшене

### 1. Проверка доступности сервисов

```bash
# Проверьте все эндпоинты
curl -X GET https://api.c0r.ai/health
curl -X GET https://ml.c0r.ai/health  
curl -X GET https://pay.c0r.ai/health

# Ожидаемый ответ для каждого:
# {"status": "healthy", "service": "api|ml|pay", "version": "0.3.8"}
```

### 2. Проверка Telegram Bot

```bash
# Проверьте бота через API
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"

# Проверьте webhook (если настроен)
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"
```

### 3. Тестирование в Telegram

#### Базовые команды:
1. Найдите бота @c0rAIBot в Telegram
2. Отправьте `/start` - должно появиться приветствие с информацией о кредитах
3. Отправьте `/help` - должен показать список команд
4. Отправьте `/status` - должен показать статус аккаунта

#### Тестирование анализа фото:
1. Отправьте фото еды боту
2. Система должна проанализировать и показать КБЖУ
3. Кредиты должны списаться (проверьте через `/status`)

#### Тестирование платежей:
1. Отправьте `/buy` - должны появиться кнопки с планами
2. Нажмите на план (Basic или Pro)
3. Должен появиться нативный Telegram инвойс
4. Используйте тестовую карту: `4111 1111 1111 1111`
5. После успешной оплаты кредиты должны добавиться

### 4. Проверка YooKassa webhook

```bash
# Проверьте webhook эндпоинт
curl -X POST https://pay.c0r.ai/webhook/yookassa \
  -H "Content-Type: application/json" \
  -d '{
    "type": "payment.succeeded",
    "event": "payment.succeeded", 
    "object": {
      "id": "test_payment_id",
      "status": "succeeded",
      "amount": {"value": "99.00", "currency": "RUB"},
      "metadata": {"telegram_user_id": "123456", "plan": "basic", "credits": "20"}
    }
  }'

# Ожидаемый ответ: {"status": "ok"}
```

### 5. Мониторинг логов

```bash
# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f api
docker-compose logs -f ml  
docker-compose logs -f pay

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 📊 Checklist для продакшена

### ✅ Инфраструктура
- [ ] Все сервисы запущены и отвечают на health checks
- [ ] SSL сертификаты установлены и работают
- [ ] Nginx проксирует запросы корректно
- [ ] Firewall настроен (только 80, 443, 22)
- [ ] Docker containers работают стабильно

### ✅ Telegram Bot
- [ ] Bot отвечает на `/start`, `/help`, `/status`
- [ ] Анализ фото работает корректно
- [ ] Кредиты списываются после анализа
- [ ] Команда `/buy` показывает кнопки оплаты
- [ ] Инвойсы создаются и отправляются

### ✅ Платежи
- [ ] YooKassa API ключи работают
- [ ] Provider token настроен правильно
- [ ] Тестовые платежи проходят успешно
- [ ] Webhook получает уведомления от YooKassa
- [ ] Кредиты добавляются после оплаты
- [ ] Пользователи получают уведомления об успешной оплате

### ✅ Интеграции
- [ ] Supabase подключение работает
- [ ] OpenAI API отвечает на запросы
- [ ] ML сервис анализирует фото
- [ ] Все межсервисные вызовы работают

## 🐛 Troubleshooting

### Проблемы с сервисами
```bash
# Перезапуск сервисов
docker-compose restart

# Пересборка при изменениях
docker-compose build --no-cache
docker-compose up -d

# Проверка ресурсов
docker stats
df -h
free -h
```

### Проблемы с SSL
```bash
# Обновление сертификатов
sudo certbot renew
sudo systemctl reload nginx

# Проверка сертификатов
sudo certbot certificates
```

### Проблемы с платежами
```bash
# Проверка YooKassa API
curl -u $YOOKASSA_SHOP_ID:$YOOKASSA_SECRET_KEY \
  https://api.yookassa.ru/v3/payments

# Проверка webhook
curl -X POST https://pay.c0r.ai/webhook/yookassa \
  -H "Content-Type: application/json" \
  -d '{"type": "test"}'
```

## 🎯 Критерии успешного деплоя

### Минимальные требования:
1. ✅ Все сервисы отвечают на health checks
2. ✅ Telegram bot работает (команды и анализ фото)
3. ✅ Платежи проходят успешно
4. ✅ Кредиты добавляются после оплаты
5. ✅ Логи не показывают критических ошибок

### Дополнительные проверки:
1. ✅ Производительность: анализ фото < 10 секунд
2. ✅ Стабильность: сервисы работают без перезапусков
3. ✅ Безопасность: только HTTPS, закрытые порты
4. ✅ Мониторинг: логи пишутся корректно

## 📞 Поддержка

После деплоя отправьте отчет:
- Статус всех сервисов
- Результаты тестирования платежей
- Логи с ошибками (если есть)
- Производительность системы

**Статус готовности**: 🟢 Готов к продакшену после получения YooKassa API ключей 