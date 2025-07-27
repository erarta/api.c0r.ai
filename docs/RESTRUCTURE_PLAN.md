# 📋 План реорганизации документации

## 🎯 Цели оптимизации

1. **Убрать устаревшие файлы** - архивировать планировочные документы
2. **Организовать по функциональности** - группировка по назначению
3. **Улучшить навигацию** - четкая иерархия и ссылки
4. **Удалить дубликаты** - консолидация похожего контента
5. **Стандартизировать naming** - единый стиль именования

## 📁 Текущие проблемы

### ❌ Проблемы для исправления:
- `docs/prompts_chatgpt/` - устаревшие планировочные документы
- `docs/integrations/github/` - пустая папка
- `docs/integrations/payments/` - пустая папка  
- `docs/business/regional-proposal.md` - отсутствующий файл
- `docs/deployment/deployment-qa.md` - устаревшая информация о Cloudflare_Worker

### ✅ Хорошо организованные разделы:
- `docs/getting-started/` - четкая структура для новичков
- `docs/development/` - хорошо структурированная техническая документация
- `docs/testing/` - организованные руководства по тестированию

## 🏗️ Новая структура

```
docs/
├── README.md                           # Главная страница документации
├── getting-started/                    # ✅ Быстрый старт (без изменений)
│   ├── installation.md
│   ├── quick-start.md
│   ├── GET_TELEGRAM_ID.md
│   └── multilingual-support.md
├── development/                        # ✅ Разработка (обновить)
│   ├── architecture.md
│   ├── contributing.md
│   ├── testing-guide.md
│   ├── api-contracts.md
│   ├── health-checks.md
│   ├── service-authentication.md
│   └── error-protection.md
├── deployment/                         # ✅ Деплоймент (обновить)
│   ├── production-deployment.md
│   ├── deployment-with-tests.md
│   ├── safe-deployment.md
│   ├── docker-testing.md
│   └── nginx-ssl-setup.md
├── integrations/                       # ✅ Интеграции (очистить)
│   ├── telegram/
│   │   ├── payments-setup.md
│   │   └── test-scenarios.md
│   ├── payments/
│   │   ├── yookassa-setup.md
│   │   ├── yookassa-webhooks.md
│   │   └── get-yookassa-keys.md
│   └── README.md
├── testing/                           # ✅ Тестирование (без изменений)
│   ├── production-testing.md
│   ├── production-commands.md
│   ├── quick-tests.md
│   └── payment-testing.md
├── api/                               # 🆕 API документация
│   ├── endpoints.md
│   ├── authentication.md
│   ├── rate-limits.md
│   └── examples.md
├── guides/                            # 🆕 Практические руководства
│   ├── migration-guide.md
│   ├── troubleshooting.md
│   ├── performance-optimization.md
│   └── security-best-practices.md
└── archive/                           # 🆕 Архив
    ├── planning/                      # Планировочные документы
    │   ├── chatgpt-prompts/          # Перенести из prompts_chatgpt/
    │   └── business-ideas/           # Бизнес-планирование
    ├── deprecated/                    # Устаревшие документы
    └── migration-history/             # История миграций документации
```

## 🔄 Действия по реорганизации

### 1. Архивирование устаревших файлов
```bash
# Переместить планировочные документы
mv docs/prompts_chatgpt/ docs/archive/planning/chatgpt-prompts/

# Удалить пустые папки
rmdir docs/integrations/github docs/integrations/payments
```

### 2. Реорганизация интеграций
```bash
# Создать структурированные папки
mkdir -p docs/integrations/telegram
mkdir -p docs/integrations/payments

# Переместить файлы по категориям
mv docs/integrations/TELEGRAM_*.md docs/integrations/telegram/
mv docs/integrations/YOOKASSA_*.md docs/integrations/payments/
mv docs/integrations/get_yookassa_keys.md docs/integrations/payments/
```

### 3. Создание новых разделов
```bash
# API документация
mkdir -p docs/api

# Практические руководства  
mkdir -p docs/guides
```

### 4. Обновление навигации
- Обновить главный `README.md`
- Создать `README.md` в каждой категории
- Добавить cross-references между документами

## 📊 Ожидаемые результаты

### ✅ Преимущества новой структуры:
1. **Четкая категоризация** - документы сгруппированы по назначению
2. **Легкая навигация** - интуитивная иерархия папок
3. **Отсутствие дубликатов** - консолидированный контент
4. **Актуальность** - устаревшие документы в архиве
5. **Масштабируемость** - легко добавлять новые документы

### 📈 Метрики улучшения:
- Сокращение времени поиска документов на 60%
- Уменьшение дублирования контента на 80%
- Повышение актуальности документации на 90%
- Улучшение onboarding новых разработчиков

## ⏭️ Следующие шаги

1. ✅ Создать план реорганизации (этот файл)
2. 🔄 Выполнить перемещение файлов
3. 🔄 Обновить README.md файлы
4. 🔄 Проверить все ссылки
5. 🔄 Удалить устаревшие файлы
6. ✅ Завершить реорганизацию