# 🚀 Деплоймент

Руководства по развертыванию c0r.AI в продакшн среде.

## 📚 Руководства в этом разделе

### 1. [Продакшн деплоймент](production-deployment.md)
Основное руководство по развертыванию:
- Подготовка серверов
- Настройка окружения
- Развертывание сервисов
- Проверка работоспособности

### 2. [Деплоймент с тестами](deployment-with-tests.md)
Развертывание с автоматическим тестированием:
- Pre-deployment тесты
- Post-deployment проверки
- Rollback стратегии
- Continuous deployment

### 3. [Безопасный деплоймент](safe-deployment.md)
Стратегии безопасного развертывания:
- Blue-green deployment
- Canary releases
- Feature flags
- Мониторинг деплоймента

### 4. [Docker тестирование](docker-testing.md)
Локальное тестирование с Docker:
- Docker Compose setup
- Локальная среда разработки
- Тестирование интеграций
- Отладка контейнеров

### 5. [NGINX SSL настройка](nginx-ssl-setup.md)
Настройка веб-сервера:
- NGINX конфигурация
- SSL сертификаты
- Reverse proxy setup
- Load balancing

## 🎯 Сценарии деплоймента

### Первичное развертывание
1. [Продакшн деплоймент](production-deployment.md) - полная настройка
2. [NGINX SSL настройка](nginx-ssl-setup.md) - веб-сервер
3. [Деплоймент с тестами](deployment-with-tests.md) - проверка

### Обновление системы
1. [Безопасный деплоймент](safe-deployment.md) - стратегия обновления
2. [Деплоймент с тестами](deployment-with-tests.md) - автотесты
3. Мониторинг и rollback при необходимости

### Локальная разработка
1. [Docker тестирование](docker-testing.md) - локальная среда
2. [Тестирование интеграций](../testing/) - проверка компонентов

## 🏗️ Архитектура деплоймента

### Продакшн среда
```
Internet → Cloudflare → NGINX → Services
                              ├── API Bot (Python)
                              ├── Edge API (Cloudflare Workers)
                              ├── ML Service (Python)
                              └── Payment Service (Python)
```

### Компоненты инфраструктуры
- **Cloudflare**: CDN, DDoS protection, Workers
- **NGINX**: Reverse proxy, SSL termination
- **Docker**: Контейнеризация сервисов
- **Supabase**: Managed database
- **GitHub Actions**: CI/CD pipeline

## 🔧 Требования к серверу

### Минимальные требования
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **OS**: Ubuntu 20.04+ / CentOS 8+

### Рекомендуемые требования
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 50GB SSD
- **Network**: 1Gbps

### Для высоких нагрузок
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Storage**: 100GB+ SSD
- **Load Balancer**: Multiple instances

## 🛠️ Инструменты деплоймента

### Автоматизация
- **GitHub Actions** - CI/CD pipeline
- **Docker Compose** - Локальная разработка
- **Ansible** - Конфигурация серверов (опционально)

### Мониторинг
- **Health checks** - Проверка состояния сервисов
- **Logs aggregation** - Централизованные логи
- **Metrics collection** - Метрики производительности

### Безопасность
- **SSL/TLS** - Шифрование трафика
- **Firewall** - Ограничение доступа
- **Secrets management** - Управление секретами

## 📋 Чеклист деплоймента

### Pre-deployment
- [ ] Backup базы данных
- [ ] Проверка тестов
- [ ] Подготовка rollback плана
- [ ] Уведомление команды

### Deployment
- [ ] Остановка старых сервисов
- [ ] Развертывание новой версии
- [ ] Применение миграций
- [ ] Запуск новых сервисов

### Post-deployment
- [ ] Health checks
- [ ] Smoke tests
- [ ] Мониторинг метрик
- [ ] Подтверждение работоспособности

## 🚨 Troubleshooting

### Частые проблемы
1. **Сервис не запускается**
   - Проверьте логи: `docker logs <container>`
   - Проверьте конфигурацию: `.env` файлы
   - Проверьте порты: `netstat -tulpn`

2. **База данных недоступна**
   - Проверьте подключение к Supabase
   - Проверьте миграции
   - Проверьте права доступа

3. **SSL проблемы**
   - Проверьте сертификаты
   - Проверьте NGINX конфигурацию
   - Обновите сертификаты

### Логи и мониторинг
```bash
# Логи сервисов
docker logs -f api-bot
docker logs -f ml-service
docker logs -f payment-service

# Системные логи
tail -f /var/log/nginx/error.log
journalctl -u docker -f

# Проверка состояния
curl http://localhost/health
docker ps -a
```

## 🔗 Связанные разделы

### Подготовка
- [Быстрый старт](../getting-started/quick-start.md)
- [Архитектура системы](../development/architecture.md)

### Тестирование
- [Продакшн тестирование](../testing/production-testing.md)
- [Быстрые тесты](../testing/quick-tests.md)

### Интеграции
- [Telegram setup](../integrations/telegram/)
- [Payment systems](../integrations/payments/)

---

**Последнее обновление**: 2025-01-21  
**Мейнтейнеры**: DevOps Team  
**Статус**: Production Ready