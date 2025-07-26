# Russian translations module loader
from .welcome import TRANSLATIONS as welcome_translations
from .help import TRANSLATIONS as help_translations
from .profile import TRANSLATIONS as profile_translations
from .payments import TRANSLATIONS as payments_translations
from .errors import TRANSLATIONS as errors_translations
from .nutrition import TRANSLATIONS as nutrition_translations
from .daily import TRANSLATIONS as daily_translations
from .recipes import TRANSLATIONS as recipes_translations
from .reports import TRANSLATIONS as reports_translations

# Combine all translations
TRANSLATIONS = {}
TRANSLATIONS.update(welcome_translations)
TRANSLATIONS.update(help_translations)
TRANSLATIONS.update(profile_translations)
TRANSLATIONS.update(payments_translations)
TRANSLATIONS.update(errors_translations)
TRANSLATIONS.update(nutrition_translations)
TRANSLATIONS.update(daily_translations)
TRANSLATIONS.update(recipes_translations)
TRANSLATIONS.update(reports_translations)