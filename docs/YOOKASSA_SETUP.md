# 💳 Настройка YooKassa для c0r.ai

## 📋 Пошаговая инструкция получения ключей YooKassa

### 1. Регистрация в YooKassa

#### Шаг 1: Создание аккаунта
1. Перейдите на [yookassa.ru](https://yookassa.ru/)
2. Нажмите **"Подключиться"**
3. Выберите **"Я предприниматель"** или **"Я организация"**
4. Заполните форму регистрации:
   - Название организации/ИП
   - ИНН
   - Контактные данные
   - Email и телефон

#### Шаг 2: Подтверждение
1. Подтвердите email адрес
2. Подтвердите телефон через SMS
3. Дождитесь модерации (обычно 1-3 рабочих дня)

### 2. Получение ключей для API

#### Шаг 1: Вход в личный кабинет
1. Войдите в [личный кабинет YooKassa](https://yookassa.ru/my/)
2. Перейдите в раздел **"Настройки"** → **"API"**

#### Шаг 2: Получение YOOKASSA_SHOP_ID
1. В разделе **"API"** найдите поле **"shopId"**
2. Скопируйте значение - это ваш `YOOKASSA_SHOP_ID`
   ```
   Пример: 123456
   ```

#### Шаг 3: Создание секретного ключа (YOOKASSA_SECRET_KEY)
1. В том же разделе **"API"** найдите **"Секретный ключ"**
2. Нажмите **"Создать ключ"** или **"Сгенерировать новый ключ"**
3. **ВАЖНО**: Сохраните ключ сразу - он показывается только один раз!
4. Скопируйте значение - это ваш `YOOKASSA_SECRET_KEY`
   ```
   Пример: live_MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTI=
   ```

### 3. Настройка Webhook URL

#### Шаг 1: Настройка уведомлений
1. В личном кабинете перейдите **"Настройки"** → **"Уведомления"**
2. В поле **"HTTP-уведомления"** укажите:
   ```
   https://pay.c0r.ai/webhook/yookassa
   ```
3. Выберите события для уведомлений:
   - ✅ **payment.succeeded** (успешная оплата)
   - ✅ **payment.canceled** (отмена платежа)
   - ✅ **refund.succeeded** (успешный возврат)

#### Шаг 2: Проверка HTTP-уведомлений
1. Нажмите **"Проверить"** рядом с URL
2. YooKassa отправит тестовый запрос
3. Убедитесь, что статус **"Активен"**

### 4. Настройка Telegram Bot Payments (YOOKASSA_PROVIDER_TOKEN)

#### Шаг 1: Связь с @BotFather
1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/mybots`
3. Выберите вашего бота
4. Нажмите **"Payments"**

#### Шаг 2: Подключение YooKassa к боту
1. Выберите **"YooKassa"** как платежную систему
2. Введите ваш `YOOKASSA_SHOP_ID` (полученный в шаге 2.2)
3. Введите ваш `YOOKASSA_SECRET_KEY` (полученный в шаге 2.3)

#### Шаг 3: Получение Provider Token
1. После успешного подключения BotFather выдаст **Provider Token**
2. Скопируйте его - это ваш `YOOKASSA_PROVIDER_TOKEN`
   ```
   Пример: 1234567890:TEST:live_MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTI=
   ```

### 5. Тестирование платежей

#### Тестовые карты YooKassa:
```
Успешная оплата:
Номер: 5555 5555 5555 4444
Срок: 12/24
CVC: 123

Отклоненная оплата:
Номер: 5555 5555 5555 4477
Срок: 12/24
CVC: 123
```

#### Проверка тестового платежа:
1. Отправьте команду `/start` боту
2. Отправьте фото еды (убедитесь что кредиты закончились)
3. Нажмите кнопку "Купить кредиты"
4. Проведите тестовый платеж
5. Проверьте логи: `docker-compose logs pay`

### 6. Обновление .env файла

Добавьте полученные ключи в ваш `.env` файл:

```env
# YooKassa Configuration
YOOKASSA_SHOP_ID=123456
YOOKASSA_SECRET_KEY=live_MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTI=
YOOKASSA_PROVIDER_TOKEN=1234567890:TEST:live_MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTI=

# Payment Configuration
YOOKASSA_PRICE_RUB=50000  # 500.00 рублей в копейках
YOOKASSA_CREDITS=50       # Количество кредитов за платеж
YOOKASSA_DESCRIPTION="50 credits for c0r.ai food analysis"
```

### 7. Налоговые настройки

#### Для работы с физическими лицами:
1. В настройках YooKassa включите **"Автоматическая отправка чеков"**
2. Настройте параметры:
   - **Система налогообложения**: УСН доходы 6%
   - **НДС**: Без НДС
   - **Способ расчета**: Полный расчет

#### Пример настройки чека в коде:
```javascript
receipt: {
  customer: {
    email: user.email // или phone
  },
  items: [{
    description: "Кредиты для анализа еды c0r.ai",
    quantity: "1.00",
    amount: {
      value: "500.00",
      currency: "RUB"
    },
    vat_code: 1 // Без НДС
  }]
}
```

### 8. Переход в продакшн

#### После тестирования:
1. В настройках YooKassa переведите в **"Боевой режим"**
2. Замените тестовые ключи на боевые
3. Обновите webhook URL на продакшн домен
4. Проведите контрольный платеж на минимальную сумму

### 🚨 Важные моменты безопасности

#### Защита ключей:
- ✅ Никогда не коммитьте секретные ключи в Git
- ✅ Используйте переменные окружения
- ✅ Ротируйте ключи каждые 6 месяцев
- ✅ Ограничьте IP-адреса для API (если возможно)

#### Проверка webhook:
```python
# Всегда проверяйте подпись webhook
import hmac
import hashlib

def verify_webhook(payload, signature, secret_key):
    expected = hmac.new(
        secret_key.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

### 📞 Поддержка

#### Если возникли проблемы:
1. **Техподдержка YooKassa**: support@yookassa.ru
2. **Документация API**: [yookassa.ru/developers](https://yookassa.ru/developers/)
3. **Telegram поддержка**: [@YooKassaSupport](https://t.me/YooKassaSupport)

#### Полезные ссылки:
- [Документация YooKassa API](https://yookassa.ru/developers/api)
- [SDK для Python](https://github.com/yoomoney/yookassa-sdk-python)
- [Примеры интеграции](https://yookassa.ru/developers/solutions)

---

**После получения всех ключей переходите к настройке платежного сервиса!** 💳 