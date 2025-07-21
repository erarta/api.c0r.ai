# Список файлов для удаления после завершения миграции

После успешного переноса всех миграций в структурированную директорию `/migrations`, следующие файлы из корневой директории могут быть безопасно удалены:

## Файлы миграций для удаления

### Основные файлы миграций
- `database_recipe_migration.sql` → перенесен в `migrations/database/2025-01-19_recipe_migration.sql`
- `database_constraints.sql` → перенесен в `migrations/database/2025-01-21_constraints.sql`
- `migration_multilingual.sql` → перенесен в `migrations/database/2025-01-21_multilingual.sql`
- `database_migrations.sql` → устаревший файл, функциональность включена в новые миграции

### Файлы rollback для удаления
- `database_recipe_migration_rollback.sql` → перенесен в `migrations/rollbacks/2025-01-19_recipe_migration_rollback.sql`
- `database_constraints_rollback.sql` → перенесен в `migrations/rollbacks/2025-01-21_constraints_rollback.sql`

### Схемы для удаления
- `schema.sql` → заменен на `migrations/schema/initial_schema.sql`

## Команды для удаления

После подтверждения, что новая структура миграций работает корректно, выполните:

```bash
# Удалить старые файлы миграций
rm database_recipe_migration.sql
rm database_constraints.sql
rm migration_multilingual.sql
rm database_migrations.sql

# Удалить старые файлы rollback
rm database_recipe_migration_rollback.sql
rm database_constraints_rollback.sql

# Удалить старую схему
rm schema.sql
```

## Проверка перед удалением

Перед удалением убедитесь, что:

1. ✅ Все миграции успешно перенесены в `/migrations/database/`
2. ✅ Все rollback файлы перенесены в `/migrations/rollbacks/`
3. ✅ Новая схема создана в `/migrations/schema/initial_schema.sql`
4. ✅ Документация обновлена в `/migrations/README.md`
5. ✅ Тесты проходят с новой структурой
6. ✅ Нет ссылок на старые файлы в коде или документации

## Статус миграции

- [x] Создана новая структура `/migrations`
- [x] Перенесены файлы миграций
- [x] Перенесены файлы rollback
- [x] Создана полная схема
- [x] Создана документация
- [ ] Протестирована новая структура
- [ ] Удалены старые файлы
- [ ] Обновлены ссылки в документации

## Примечания

- Не удаляйте файлы до полного тестирования новой структуры
- Создайте резервную копию перед удалением
- Проверьте, что нет скриптов, ссылающихся на старые файлы