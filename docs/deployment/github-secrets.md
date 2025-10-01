# GitHub Secrets Configuration
*Added by Claude for automated deployment*

## Required Secrets for Production Deployment

Добавь эти секреты в GitHub Repository Settings → Secrets and variables → Actions:

### Server Access
```
PRODUCTION_SSH_KEY     # Private SSH key для доступа к продакшн серверу
PRODUCTION_HOST        # IP адрес продакшн сервера (ec2-56-228-31-230.eu-north-1.compute.amazonaws.com)
```

### Database Access
```
DB_HOST               # aws-0-eu-central-1.pooler.supabase.com
DB_USER               # postgres.mmrzpngugivxoapjiovb
DB_PASSWORD           # xuoO4|LSaaGX5
DB_NAME               # postgres
DB_PORT               # 6543
```

### Application Secrets
```
TELEGRAM_BOT_TOKEN    # 7918860162:AAHbyAcvFIUwQCdq1jq6keVP9OJz2Q6HJmA
SUPABASE_SERVICE_KEY  # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
INTERNAL_API_TOKEN    # KQdA2RkM9m2q9j6k3TQd2fN7WqY8eE5rP1xL0sV4hZ6uC3nF8pB4jM2vH9yT7aQ1
```

## Workflow Process

1. **Pre-deployment**: Применяет миграции к БД
2. **Validation**: Проверяет конфигурацию
3. **Deployment**: Обновляет код и перезапускает контейнеры
4. **Testing**: Проверяет работоспособность API
5. **Notification**: Уведомляет о статусе деплоя

## Migration Strategy

### SQL Migrations
- Файлы в `migrations/database/*.sql` применяются автоматически
- Используется convention: `YYYY-MM-DD_description.sql`

### Python Migrations
- Файл `migrations/run_migrations.py` запускается если существует
- Используется для сложных миграций данных

### Rollback Strategy
- Создавай rollback файлы: `YYYY-MM-DD_rollback_description.sql`
- В случае проблем можно быстро откатиться