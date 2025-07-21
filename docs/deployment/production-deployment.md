# 🚀 Продакшн деплоймент c0r.AI

Полное руководство по развертыванию c0r.AI в продакшн среде.

## 📋 Предварительные требования

### 1. Серверная инфраструктура
- **Instance Type**: t3.medium или выше (минимум 4GB RAM)
- **OS**: Ubuntu 22.04 LTS
- **Storage**: 20GB+ SSD
- **Security Group**: Порты 22 (SSH), 80 (HTTP), 443 (HTTPS)

### 2. Доменная конфигурация
Настройте DNS A записи для вашего домена:
```
api.c0r.ai  → Your_EC2_Public_IP
ml.c0r.ai   → Your_EC2_Public_IP  
pay.c0r.ai  → Your_EC2_Public_IP
```

### 3. Необходимые сервисы
- Supabase проект (база данных)
- Telegram Bot Token
- OpenAI API ключ
- YooKassa аккаунт (для платежей)

## 🔧 Настройка сервера

### 1. Подключение к серверу
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2. Установка зависимостей
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Установка Nginx
sudo apt install nginx -y

# Установка Certbot для SSL
sudo apt install certbot python3-certbot-nginx -y

# Установка Git
sudo apt install git -y
```

### 3. Клонирование репозитория
```bash
cd /home/ubuntu
git clone https://github.com/yourusername/api.c0r.ai.git
cd api.c0r.ai
```

### 4. Конфигурация окружения
```bash
# Копирование шаблона продакшн окружения
cp .env.production.example .env

# Редактирование переменных окружения
nano .env
```

**Обязательные переменные для обновления:**
```env
# Telegram
TELEGRAM_BOT_TOKEN=your_production_bot_token
TELEGRAM_SERVICE_BOT_TOKEN=your_service_bot_token

# Supabase
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Внутренняя аутентификация
INTERNAL_API_TOKEN=generate_secure_token_here

# YooKassa
YOOKASSA_SHOP_ID=your_yookassa_shop_id
YOOKASSA_SECRET_KEY=your_yookassa_secret_key
YOOKASSA_PROVIDER_TOKEN=your_yookassa_provider_token

# Продакшн URLs (автоматически настраиваются)
ML_SERVICE_URL=https://ml.c0r.ai
PAY_SERVICE_URL=https://pay.c0r.ai
```

**Генерация безопасного токена:**
```bash
# Генерация INTERNAL_API_TOKEN
openssl rand -hex 32
```

**Альтернативный способ - скрипт переключения окружения:**
```bash
# Переключение на продакшн URLs
./scripts/switch-env.sh prod

# Переключение обратно на разработку (если нужно)
./scripts/switch-env.sh dev
```

## 🌐 Настройка веб-сервера

### 1. Временная HTTP конфигурация Nginx
```bash
# Удаление конфигурации по умолчанию
sudo rm /etc/nginx/sites-enabled/default

# Копирование временной HTTP конфигурации
cd /home/ubuntu/api.c0r.ai
sudo cp nginx.conf.temp /etc/nginx/sites-available/c0r.ai
sudo ln -s /etc/nginx/sites-available/c0r.ai /etc/nginx/sites-enabled/

# Создание web root для certbot
sudo mkdir -p /var/www/html

# Тестирование конфигурации
sudo nginx -t

# Если конфигурация OK, перезагрузка nginx
sudo systemctl reload nginx
```

### 2. Запуск сервисов
```bash
# Сборка и запуск всех сервисов
docker-compose build
docker-compose up -d

# Проверка статуса
docker-compose ps
docker-compose logs
```

### 3. Получение SSL сертификатов
```bash
# Получение сертификатов для всех поддоменов
sudo certbot --nginx -d api.c0r.ai -d ml.c0r.ai -d pay.c0r.ai

# Настройка автообновления
sudo crontab -e
# Добавить строку: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 4. Переключение на продакшн SSL конфигурацию
```bash
# Копирование продакшн SSL конфигурации
sudo cp nginx.conf.production /etc/nginx/sites-available/c0r.ai

# Тестирование конфигурации
sudo nginx -t

# Если конфигурация OK, перезагрузка nginx
sudo systemctl reload nginx
```

### 5. Настройка файрвола
```bash
# Настройка UFW
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

## 🤖 Настройка GitHub Actions

### 1. Секреты репозитория
Добавьте эти секреты в ваш GitHub репозиторий (Settings → Secrets and variables → Actions):

- `EC2_SSH_KEY` - Содержимое приватного ключа EC2
- `EC2_USER` - `ubuntu`
- `EC2_HOST` - Публичный IP или домен EC2

### 2. Генерация SSH ключа для деплоймента
```bash
# На локальной машине
ssh-keygen -t rsa -b 4096 -f ~/.ssh/c0r_ai_deploy

# Копирование публичного ключа на EC2
ssh-copy-id -i ~/.ssh/c0r_ai_deploy.pub ubuntu@your-ec2-ip

# Добавление содержимого приватного ключа в GitHub секреты
cat ~/.ssh/c0r_ai_deploy
```

### 3. Тестирование деплоймента
```bash
git add .
git commit -m "feat: setup production deployment"
git push origin main
```

## 🧪 Тестирование продакшн среды

### ⚡ Быстрая проверка (5 минут)

#### 1. Предварительная проверка
```bash
# Тест подключения к боту
python test_bot_connection.py

# Тест подключения к базе данных
python test_db_connection.py

# Проверка запущенных сервисов
docker-compose ps
```

#### 2. Запуск мониторинга
```bash
# Мониторинг ошибок (рекомендуется для продакшн)
./monitor_bot.sh errors

# Или комплексный мониторинг
./monitor_bot.sh all

# Быстрая проверка статистики
./monitor_bot.sh stats
```

### 📱 Последовательность тестирования в Telegram

#### Фаза 1: Базовые команды (2 мин)
```
/start    → Приветственное сообщение с кнопками
/help     → Полное руководство помощи
/status   → Информация о пользователе, кредиты, дата регистрации
```

#### Фаза 2: Настройка профиля (3 мин)
```
/profile  → Начать настройку профиля
          → Возраст: 25
          → Пол: Мужской
          → Рост: 180
          → Вес: 75
          → Активность: Умеренно активный
          → Цель: Поддержание веса
```

#### Фаза 3: Анализ фото (2 мин)
- Отправить фото еды → Результаты анализа + прогресс
- Отправить не-еду → Сообщение "Еда не обнаружена"

#### Фаза 4: Продвинутые функции (2 мин)
```
/daily    → Дневной прогресс с калориями
/buy      → Варианты оплаты с кнопками
```

#### Фаза 5: Стресс-тест (1 мин)
- Отправить 6 фото быстро → Ограничение скорости после 5-го фото

## 🔍 Мониторинг и обслуживание

### Проверки работоспособности
```bash
# Проверка статуса сервисов
curl https://api.c0r.ai/
curl https://ml.c0r.ai/
curl https://pay.c0r.ai/

# Проверка логов
docker-compose logs -f api
docker-compose logs -f ml
docker-compose logs -f pay
```

### Мониторинг в реальном времени
```bash
# Все ошибки (рекомендуется)
./monitor_bot.sh errors

# Активность пользователей
./monitor_bot.sh users

# Все логи с цветами
./monitor_bot.sh logs

# Метрики производительности
./monitor_bot.sh performance
```

### Мониторинг системы
```bash
# Проверка системных ресурсов
htop
df -h
docker system df

# Очистка старых образов
docker system prune -f

# Статистика Docker
docker stats
```

### Стратегия резервного копирования
```bash
# Резервное копирование файла окружения
cp .env .env.backup.$(date +%Y%m%d)

# Резервное копирование базы данных (если используется локальная БД)
# Настройте резервные копии Supabase в панели управления
```

## 🚨 Устранение неполадок

### Частые проблемы

#### Сервисы не запускаются:
```bash
docker-compose logs [service-name]
docker-compose down && docker-compose up -d
```

#### Бот не отвечает:
```bash
# Перезапуск бота
docker-compose restart api

# Проверка статуса
docker-compose ps

# Просмотр последних логов
docker-compose logs --tail=20 api
```

#### Проблемы с SSL сертификатами:
```bash
sudo certbot renew --dry-run
sudo nginx -t && sudo systemctl reload nginx
```

#### Высокое использование памяти:
```bash
docker system prune -f
sudo systemctl restart docker
```

#### Проблемы с базой данных:
```bash
# Тест базы данных
python test_db_connection.py

# Проверка сервиса базы данных
docker-compose logs db
```

### Расположение логов
- Nginx: `/var/log/nginx/`
- Docker: `docker-compose logs`
- Система: `journalctl -u docker`

### Экстренные команды
```bash
# Быстрый мониторинг
./monitor_bot.sh errors

# Проверка что все работает
docker-compose ps && ./monitor_bot.sh stats

# Перезапуск при необходимости
docker-compose restart api && docker-compose logs -f api
```

## 📊 Индикаторы успеха

### ✅ Бот работает хорошо
- Команды отвечают в течение 3 секунд
- Анализ фото завершается в течение 30 секунд
- Настройка профиля работает гладко
- Ограничение скорости предотвращает спам
- Нет ошибок в логах
- Операции с базой данных успешны

### ❌ Предупреждающие знаки
- Время отклика > 10 секунд
- ERROR сообщения в логах
- Сбои анализа фото
- Проблемы подключения к базе данных
- Постоянно растущее использование памяти

## 🔒 Соображения безопасности

### 1. Переменные окружения
- Никогда не коммитьте `.env` в репозиторий
- Используйте сильный `INTERNAL_API_TOKEN`
- Регулярно меняйте API ключи

### 2. Безопасность Nginx
- Настроено ограничение скорости для каждого сервиса
- Включены заголовки безопасности
- Автообновление SSL сертификатов

### 3. Безопасность Docker
- Сервисы работают в изолированных контейнерах
- Нет root привилегий в контейнерах
- Только внутренняя сетевая коммуникация

## 📊 Оптимизация производительности

### 1. Оптимизация Docker
```yaml
# Добавить в docker-compose.yml для продакшн
version: '3.8'
services:
  api:
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### 2. Оптимизация Nginx
```nginx
# Добавить в nginx.conf
gzip on;
gzip_types text/plain application/json;
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;
```

## 📋 Чеклист тестирования

### Перед продакшн
- [ ] Переменные окружения настроены
- [ ] Подключение к базе данных работает
- [ ] Токен бота действителен
- [ ] ML сервис доступен
- [ ] Docker сервисы запущены

### Во время тестирования
- [ ] Команда /start работает
- [ ] Настройка профиля завершается
- [ ] Анализ фото функционален
- [ ] Ограничение скорости активно
- [ ] Нет ошибок в логах
- [ ] Производительность приемлема

### После тестирования
- [ ] Проверить логи ошибок
- [ ] Проверить записи в базе данных
- [ ] Мониторить системные ресурсы
- [ ] Документировать любые проблемы

## 🎯 Следующие шаги

1. **Настройка мониторинга**: Настроить Grafana/Prometheus
2. **Балансировка нагрузки**: Добавить несколько инстансов при необходимости
3. **CDN**: Настроить Cloudflare для статических ресурсов
4. **Масштабирование базы данных**: Оптимизировать конфигурацию Supabase
5. **Интеграция платежей**: Завершить настройку YooKassa

## 📞 Поддержка

При проблемах с деплойментом:
1. Проверьте логи: `docker-compose logs -f`
2. Проверьте переменные окружения
3. Тестируйте сетевое подключение
4. Проверьте SSL сертификаты

### Файлы для проверки
- `PRODUCTION_TESTING_COMMANDS.md` - Детальное руководство по тестированию
- `QUICK_PROD_TEST.md` - Быстрый 10-минутный тест
- `TESTING_GUIDE.md` - Тестирование локальной разработки
- `CHANGELOG.md` - Последние изменения и исправления

---

**🎉 Ваш c0r.ai бот готов к продакшн!**

**Общее время настройки: ~30 минут**  
**Общее время тестирования: ~10 минут**  
**Статус**: Готов к продакшн развертыванию! 🚀