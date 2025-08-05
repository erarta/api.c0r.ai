# Пошаговый чеклист реализации AIDI.APP

*Дата создания: 27 января 2025*
*Цель: Детальная инструкция по ребрендингу c0r.ai в AIDI.APP*

## 📋 Обзор процесса

Этот чеклист поможет вам пошагово выполнить ребрендинг сервиса анализа питания c0r.ai в сервис репутации и KYC AIDI.APP. Процесс разделен на 8 основных этапов с детальными инструкциями.

**Примерное время выполнения:** 4-6 недель  
**Команда:** 3-5 разработчиков  
**Бюджет:** $50,000-80,000

## 🎯 Этап 1: Подготовка и планирование (Неделя 1)

### 1.1 Создание новых аккаунтов и сервисов

#### Telegram Bot
- [ ] **Создать нового бота через @BotFather**
  ```
  /newbot
  Имя: AIDI Reputation Bot
  Username: @AIDIReputationBot
  ```
- [ ] **Создать сервисного бота для уведомлений**
  ```
  /newbot
  Имя: AIDI Service Bot
  Username: @AIDIServiceBot
  ```
- [ ] **Настроить команды бота**
  ```
  /setcommands
  start - Запустить бота
  help - Помощь и FAQ
  profile - Профиль пользователя
  balance - Баланс кредитов
  history - История анализов
  settings - Настройки
  language - Изменить язык
  support - Поддержка
  ```
- [ ] **Настроить описание бота**
  ```
  /setdescription
  🛡️ AIDI.APP - AI-powered reputation analysis and deepfake detection service
  
  🔍 Reputation Analysis - Comprehensive digital footprint assessment
  🎭 Deepfake Detection - Advanced media verification
  🔐 KYC Verification - Identity validation services
  ```

#### Supabase Database
- [ ] **Создать новый проект Supabase**
  - Название: `aidi-app-production`
  - Регион: `East US (North Virginia)`
  - План: `Pro ($25/month)`
- [ ] **Настроить RLS (Row Level Security)**
- [ ] **Создать API ключи**
  - Anon key (для клиентских запросов)
  - Service role key (для серверных операций)
- [ ] **Настроить бэкапы**
  - Ежедневные автоматические бэкапы
  - Point-in-time recovery

#### Cloudflare R2 Storage
- [ ] **Создать аккаунт Cloudflare**
- [ ] **Настроить R2 buckets**
  ```
  aidi-uploads (пользовательские загрузки)
  aidi-reports (сгенерированные отчеты)
  aidi-backups (резервные копии)
  aidi-logs (логи приложения)
  ```
- [ ] **Настроить CORS политики**
- [ ] **Создать API токены**

#### Домены и SSL
- [ ] **Зарегистрировать домен aidi.app**
- [ ] **Настроить DNS записи**
  ```
  A     aidi.app           → IP сервера
  CNAME api.aidi.app      → aidi.app
  CNAME ml.aidi.app       → aidi.app
  CNAME pay.aidi.app      → aidi.app
  CNAME uploads.aidi.app  → R2 bucket
  ```
- [ ] **Получить SSL сертификаты**
  - Let's Encrypt или Cloudflare SSL

### 1.2 AI сервисы и API ключи

#### Gemini AI
- [ ] **Создать аккаунт Google AI Studio**
- [ ] **Получить API ключ Gemini**
- [ ] **Настроить квоты и лимиты**
- [ ] **Протестировать API**

#### OpenAI
- [ ] **Создать аккаунт OpenAI**
- [ ] **Получить API ключ**
- [ ] **Настроить биллинг**
- [ ] **Протестировать GPT-4 Vision API**

#### Социальные сети API
- [ ] **VK API** - получить токен для поиска пользователей
- [ ] **Telegram API** - настроить для поиска каналов
- [ ] **Instagram Basic Display API** (опционально)
- [ ] **LinkedIn API** (опционально)

### 1.3 Платежные системы

#### Stripe (международные платежи)
- [ ] **Создать аккаунт Stripe**
- [ ] **Настроить продукты и цены**
  ```
  Starter Package: $19.99 (10 credits)
  Professional Package: $99.99 (100 credits + bonuses)
  ```
- [ ] **Настроить webhooks**
  - URL: `https://pay.aidi.app/stripe/webhook`
  - События: `payment_intent.succeeded`, `payment_intent.payment_failed`
- [ ] **Получить API ключи**

#### YooKassa (российские платежи)
- [ ] **Создать аккаунт YooKassa**
- [ ] **Пройти модерацию**
- [ ] **Настроить продукты и цены**
  ```
  Базовый пакет: 990₽ (10 кредитов)
  Профессиональный пакет: 4990₽ (100 кредитов + бонусы)
  ```
- [ ] **Настроить webhooks**
- [ ] **Интегрировать с Telegram Payments**

## 🗄️ Этап 2: Миграция базы данных (Неделя 2)

### 2.1 Подготовка к миграции

- [ ] **Создать полный бэкап текущей БД c0r.ai**
  ```bash
  pg_dump -h [supabase_host] -U [user] -d [database] > c0r_ai_backup_$(date +%Y%m%d).sql
  ```
- [ ] **Проанализировать зависимости данных**
- [ ] **Подготовить план отката (rollback)**
- [ ] **Уведомить пользователей о техническом обслуживании**

### 2.2 Выполнение миграции

- [ ] **Запустить скрипт миграции**
  ```bash
  python scripts/migrate_to_aidi.py
  ```
- [ ] **Выполнить SQL миграции по порядку:**
  1. `2025-01-27_update_users_for_aidi.sql`
  2. `2025-01-27_update_user_profiles_for_aidi.sql`
  3. `2025-01-27_create_reputation_analyses.sql`
  4. `2025-01-27_create_deepfake_detections.sql`
  5. `2025-01-27_create_reputation_sources.sql`
  6. `2025-01-27_create_kyc_verifications.sql`
  7. `2025-01-27_update_credits_system.sql`
  8. `2025-01-27_create_analytics_views.sql`
  9. `2025-01-27_cleanup_nutrition_tables.sql`

### 2.3 Проверка миграции

- [ ] **Проверить целостность данных**
  ```sql
  SELECT COUNT(*) FROM users;
  SELECT COUNT(*) FROM user_profiles;
  SELECT COUNT(*) FROM credits;
  SELECT COUNT(*) FROM payments;
  ```
- [ ] **Протестировать новые таблицы**
- [ ] **Проверить индексы и производительность**
- [ ] **Запустить тесты приложения**

## 💻 Этап 3: Разработка кода (Недели 3-4)

### 3.1 Обновление API Service

#### Telegram Bot Handlers
- [ ] **Обновить handlers/default.py**
  - Главное меню с новыми опциями
  - Приветственные сообщения
  - Навигация между состояниями

- [ ] **Создать handlers/reputation.py**
  ```python
  # Основные функции:
  - handle_reputation_menu()
  - handle_data_input()
  - handle_analysis_start()
  - handle_analysis_results()
  - handle_report_download()
  ```

- [ ] **Создать handlers/deepfake.py**
  ```python
  # Основные функции:
  - handle_deepfake_menu()
  - handle_media_upload()
  - handle_detection_start()
  - handle_detection_results()
  ```

- [ ] **Обновить handlers/profile.py**
  - Новые поля профиля
  - Статистика по репутации и дипфейкам
  - Настройки анализа

#### FSM States
- [ ] **Создать states/reputation.py**
  ```python
  class ReputationStates(StatesGroup):
      waiting_for_input = State()
      entering_name = State()
      entering_phone = State()
      entering_email = State()
      uploading_photo = State()
      confirming_analysis = State()
      processing = State()
      viewing_results = State()
  ```

- [ ] **Создать states/deepfake.py**
  ```python
  class DeepfakeStates(StatesGroup):
      waiting_for_media = State()
      uploading_media = State()
      selecting_analysis_type = State()
      processing = State()
      viewing_results = State()
  ```

#### Keyboards
- [ ] **Обновить keyboards/default.py**
  - Новое главное меню
  - Кнопки репутации и дипфейков

- [ ] **Создать keyboards/reputation.py**
  - Меню типов анализа
  - Кнопки ввода данных
  - Навигация по результатам

- [ ] **Создать keyboards/deepfake.py**
  - Меню типов детекции
  - Кнопки загрузки медиа
  - Результаты анализа

### 3.2 Обновление ML Service

#### Reputation Analysis
- [ ] **Создать ml/reputation/analyzer.py**
  ```python
  class ReputationAnalyzer:
      def analyze_person(self, data: dict) -> dict
      def collect_social_data(self, name: str) -> dict
      def check_public_records(self, name: str) -> dict
      def search_news_mentions(self, name: str) -> dict
      def calculate_scores(self, data: dict) -> dict
  ```

- [ ] **Создать ml/reputation/data_sources/**
  - `social_media.py` - интеграция с VK, Telegram
  - `public_registries.py` - ЕГРЮЛ, суды
  - `news_sources.py` - поиск в новостях
  - `court_records.py` - судебные решения

- [ ] **Создать ml/reputation/scoring/**
  - `risk_calculator.py` - расчет риск-скора
  - `sentiment_analyzer.py` - анализ тональности
  - `credibility_scorer.py` - оценка достоверности

#### Deepfake Detection
- [ ] **Создать ml/deepfake/detector.py**
  ```python
  class DeepfakeDetector:
      def detect_deepfake(self, media_url: str) -> dict
      def analyze_video(self, video_path: str) -> dict
      def analyze_image(self, image_path: str) -> dict
      def generate_report(self, results: dict) -> dict
  ```

- [ ] **Создать ml/deepfake/models/**
  - `face_detection.py` - детекция лиц
  - `temporal_analysis.py` - временные несоответствия
  - `artifact_detection.py` - артефакты сжатия

#### AI Clients
- [ ] **Обновить ml/ai_clients/gemini/client.py**
  ```python
  class GeminiReputationClient:
      def analyze_reputation_data(self, data: dict) -> dict
      def analyze_sentiment(self, text: str) -> float
      def extract_key_facts(self, content: str) -> list
  ```

- [ ] **Обновить ml/ai_clients/openai/client.py**
  ```python
  class OpenAIDeepfakeClient:
      def detect_deepfake_image(self, image_url: str) -> dict
      def analyze_video_frame(self, frame_data: bytes) -> dict
      def generate_explanation(self, results: dict) -> str
  ```

### 3.3 Обновление Payment Service

- [ ] **Обновить конфигурацию продуктов**
  ```python
  CREDIT_PACKAGES = {
      'basic_ru': {'credits': 10, 'price': 990, 'currency': 'RUB'},
      'pro_ru': {'credits': 100, 'bonus': 20, 'price': 4990, 'currency': 'RUB'},
      'basic_intl': {'credits': 10, 'price': 19.99, 'currency': 'USD'},
      'pro_intl': {'credits': 100, 'bonus': 25, 'price': 99.99, 'currency': 'USD'}
  }
  ```

- [ ] **Обновить webhook обработчики**
  - Новые типы транзакций кредитов
  - Уведомления о покупках

### 3.4 Интернационализация

- [ ] **Обновить переводы согласно документу 06_I18N_UPDATES.md**
  - Заменить модули питания на репутацию/дипфейки
  - Добавить новую терминологию кибербезопасности
  - Протестировать все переводы

## 🧪 Этап 4: Тестирование (Неделя 5)

### 4.1 Unit тесты

- [ ] **Создать тесты для reputation analysis**
  ```python
  # tests/unit/test_reputation_analysis.py
  def test_basic_reputation_analysis()
  def test_extended_reputation_analysis()
  def test_risk_score_calculation()
  def test_sentiment_analysis()
  ```

- [ ] **Создать тесты для deepfake detection**
  ```python
  # tests/unit/test_deepfake_detection.py
  def test_image_deepfake_detection()
  def test_video_deepfake_detection()
  def test_confidence_scoring()
  ```

- [ ] **Создать тесты для FSM states**
  ```python
  # tests/unit/test_bot_states.py
  def test_reputation_state_transitions()
  def test_deepfake_state_transitions()
  def test_default_state_navigation()
  ```

### 4.2 Integration тесты

- [ ] **Тестирование API endpoints**
  ```bash
  pytest tests/integration/test_reputation_api.py -v
  pytest tests/integration/test_deepfake_api.py -v
  pytest tests/integration/test_payment_flow.py -v
  ```

- [ ] **Тестирование Telegram bot**
  ```python
  # tests/integration/test_telegram_bot.py
  def test_reputation_analysis_flow()
  def test_deepfake_detection_flow()
  def test_payment_integration()
  ```

### 4.3 E2E тестирование

- [ ] **Полный пользовательский сценарий**
  1. Регистрация нового пользователя
  2. Покупка кредитов
  3. Анализ репутации (базовый и расширенный)
  4. Детекция дипфейка (быстрая и детальная)
  5. Просмотр истории и отчетов

- [ ] **Нагрузочное тестирование**
  ```bash
  # Тест 100 одновременных пользователей
  locust -f tests/load/test_reputation_load.py --host=https://api.aidi.app
  ```

## 🚀 Этап 5: Развертывание инфраструктуры (Неделя 5)

### 5.1 AWS Infrastructure

- [ ] **Создать VPC и сети**
  ```bash
  # Использовать Terraform или CloudFormation
  terraform apply -var-file="production.tfvars"
  ```

- [ ] **Запустить EC2 инстансы**
  - 3 × t3.large для API Service
  - 2 × c5.xlarge для ML Service  
  - 2 × t3.medium для Payment Service

- [ ] **Настроить Load Balancer**
  - Application Load Balancer
  - Health checks для всех сервисов
  - SSL termination

- [ ] **Настроить Auto Scaling Groups**
  - Минимум 2, максимум 5 инстансов для API
  - Минимум 1, максимум 4 инстанса для ML
  - Минимум 1, максимум 3 инстанса для Payment

### 5.2 Database и Cache

- [ ] **Настроить Redis ElastiCache**
  - 3-node кластер
  - Репликация и failover
  - Backup и monitoring

- [ ] **Настроить Supabase connection pooling**
  - PgBouncer конфигурация
  - Read replicas для масштабирования

### 5.3 Мониторинг

- [ ] **Развернуть Prometheus + Grafana**
  ```bash
  docker-compose -f monitoring/docker-compose.yml up -d
  ```

- [ ] **Настроить алерты**
  - High error rate (>5%)
  - High response time (>2s)
  - Service down
  - Database connections high (>80%)

- [ ] **Настроить логирование**
  - Centralized logging с ELK stack
  - Structured JSON logs
  - Log rotation и retention

## 🔧 Этап 6: Конфигурация и деплой (Неделя 6)

### 6.1 Environment Configuration

- [ ] **Настроить production переменные**
  ```bash
  # Скопировать из 07_DEPLOYMENT_INFRASTRUCTURE.md
  cp .env.production.example .env.production
  # Заполнить все необходимые ключи
  ```

- [ ] **Настроить Docker images**
  ```bash
  # Build и push в ECR
  docker build -t aidi/api:v1.0.0 ./services/api
  docker build -t aidi/ml:v1.0.0 ./services/ml
  docker build -t aidi/payment:v1.0.0 ./services/pay
  ```

### 6.2 Deployment

- [ ] **Развернуть сервисы**
  ```bash
  # На каждом сервере
  docker-compose -f docker-compose.prod.yml up -d
  ```

- [ ] **Настроить Nginx reverse proxy**
  ```bash
  # Скопировать конфигурацию из документации
  sudo cp nginx.conf /etc/nginx/sites-available/aidi.app
  sudo ln -s /etc/nginx/sites-available/aidi.app /etc/nginx/sites-enabled/
  sudo nginx -t && sudo systemctl reload nginx
  ```

- [ ] **Настроить SSL сертификаты**
  ```bash
  sudo certbot --nginx -d aidi.app -d api.aidi.app -d ml.aidi.app -d pay.aidi.app
  ```

### 6.3 Health Checks

- [ ] **Проверить все endpoints**
  ```bash
  curl https://api.aidi.app/health
  curl https://ml.aidi.app/health  
  curl https://pay.aidi.app/health
  ```

- [ ] **Проверить Telegram webhook**
  ```bash
  curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
       -d "url=https://api.aidi.app/webhook/telegram"
  ```

- [ ] **Протестировать платежи**
  - Тестовый платеж через Stripe
  - Тестовый платеж через YooKassa

## 📱 Этап 7: Тестирование в продакшене (Неделя 6)

### 7.1 Closed Beta

- [ ] **Пригласить 50 beta-тестеров**
  - 25 из России (YooKassa)
  - 25 международных (Stripe)

- [ ] **Провести тестирование основных сценариев**
  - Регистрация и onboarding
  - Покупка кредитов
  - Анализ репутации (все типы)
  - Детекция дипфейков (все типы)
  - Техническая поддержка

- [ ] **Собрать фидбек и исправить критические баги**

### 7.2 Performance Testing

- [ ] **Нагрузочное тестирование**
  - 100 одновременных пользователей
  - 1000 анализов в час
  - Проверка автомасштабирования

- [ ] **Мониторинг производительности**
  - Response time < 2 секунд
  - Error rate < 1%
  - Uptime > 99.5%

### 7.3 Security Audit

- [ ] **Penetration testing**
- [ ] **OWASP security checklist**
- [ ] **Data privacy compliance (GDPR, 152-ФЗ)**
- [ ] **API security testing**

## 🎉 Этап 8: Запуск и маркетинг (Неделя 7+)

### 8.1 Soft Launch

- [ ] **Объявить о ребрендинге существующим пользователям c0r.ai**
  - Email рассылка
  - Уведомления в боте
  - Миграция аккаунтов

- [ ] **Запустить AIDI.APP для новых пользователей**
  - Обновить все ссылки и документацию
  - Запустить рекламные кампании

### 8.2 Marketing Campaign

- [ ] **Контент-маркетинг**
  - Блог посты о кибербезопасности
  - Кейсы использования
  - YouTube видео с демо

- [ ] **Социальные сети**
  - Telegram каналы и чаты
  - LinkedIn для B2B аудитории
  - VK для российского рынка

- [ ] **Партнерства**
  - HR-платформы
  - Кибербезопасность сообщества
  - Финтех компании

### 8.3 Мониторинг и оптимизация

- [ ] **Отслеживать ключевые метрики**
  - DAU/MAU
  - Конверсия в платящих пользователей
  - ARPU
  - Churn rate

- [ ] **A/B тестирование**
  - Onboarding flow
  - Pricing страницы
  - Bot интерфейс

- [ ] **Непрерывная оптимизация**
  - Производительность AI моделей
  - Скорость анализа
  - Точность результатов

## 🔄 Post-Launch Roadmap

### Месяц 1-2: Стабилизация
- [ ] Исправление багов на основе пользовательского фидбека
- [ ] Оптимизация производительности
- [ ] Расширение источников данных для репутационного анализа

### Месяц 3-4: Новые функции
- [ ] KYC верификация документов
- [ ] API для B2B клиентов
- [ ] Мобильное приложение

### Месяц 5-6: Масштабирование
- [ ] Международная экспансия
- [ ] Корпоративные тарифы
- [ ] White-label решения

## 📞 Поддержка и контакты

### Техническая поддержка
- **Telegram:** @AIDISupport
- **Email:** support@aidi.app
- **Документация:** https://docs.aidi.app

### Экстренные контакты
- **DevOps:** +7-XXX-XXX-XXXX
- **Security:** security@aidi.app
- **Business:** business@aidi.app

## ✅ Финальный чеклист готовности

Перед запуском убедитесь, что выполнены все пункты:

### Техническая готовность
- [ ] Все сервисы развернуты и работают
- [ ] База данных мигрирована успешно
- [ ] Мониторинг и алерты настроены
- [ ] Бэкапы настроены и протестированы
- [ ] SSL сертификаты установлены
- [ ] DNS записи настроены корректно

### Функциональная готовность
- [ ] Telegram bot отвечает на все команды
- [ ] Анализ репутации работает корректно
- [ ] Детекция дипфейков функционирует
- [ ] Платежи проходят успешно (Stripe + YooKassa)
- [ ] Все переводы актуальны
- [ ] Отчеты генерируются корректно

### Бизнес готовность
- [ ] Ценообразование настроено
- [ ] Юридические документы обновлены
- [ ] Политика конфиденциальности актуальна
- [ ] Команда поддержки обучена
- [ ] Маркетинговые материалы готовы
- [ ] Партнерские соглашения подписаны

**🎯 После выполнения всех пунктов чеклиста AIDI.APP готов к запуску!**

---

*Этот чеклист является живым документом и должен обновляться по мере выполнения задач и появления новых требований.*