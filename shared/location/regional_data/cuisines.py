"""
Regional Cuisines Database for c0r.AI
Comprehensive database of regional food cultures and cuisines
"""

from typing import Dict, List, Any
from datetime import datetime


# Региональные кухни и их характеристики
REGIONAL_CUISINES = {
    "RU": {
        "cuisine_types": ["русская", "советская", "кавказская", "сибирская"],
        "common_products": [
            # Крупы и злаки
            "гречка", "рис", "овсянка", "пшено", "перловка", "манка",
            # Овощи
            "картофель", "морковь", "лук", "капуста", "свекла", "огурцы", "помидоры",
            "чеснок", "укроп", "петрушка", "зеленый лук",
            # Мясо и рыба
            "говядина", "свинина", "курица", "рыба", "сельдь", "скумбрия",
            # Молочные продукты
            "молоко", "творог", "сметана", "кефир", "ряженка", "простокваша",
            # Хлебобулочные
            "хлеб", "батон", "сушки", "баранки",
            # Другое
            "яйца", "подсолнечное масло", "сливочное масло", "соль", "сахар"
        ],
        "seasonal_products": {
            "spring": ["редис", "зеленый лук", "укроп", "петрушка", "щавель", "крапива"],
            "summer": ["огурцы", "помидоры", "кабачки", "баклажаны", "перец", "ягоды", "фрукты", "зелень"],
            "autumn": ["тыква", "яблоки", "груши", "грибы", "капуста", "морковь", "свекла"],
            "winter": ["квашеная капуста", "соленые огурцы", "варенье", "компоты", "сушеные грибы"]
        },
        "cooking_methods": [
            "варка", "жарка", "тушение", "запекание", "парка", 
            "засолка", "квашение", "сушка", "копчение", "маринование"
        ],
        "measurement_units": "metric",
        "dietary_preferences": ["без ограничений", "постная еда", "домашняя кухня"],
        "food_culture_notes": "Традиционная русская кухня с акцентом на сытные блюда, супы, каши и консервацию. Важную роль играют сезонные заготовки и домашние традиции.",
        "region_code": "RU"
    },
    
    "US": {
        "cuisine_types": ["американская", "мексиканская", "итальянская", "азиатская"],
        "common_products": [
            # Мясо и птица
            "beef", "chicken", "pork", "turkey", "bacon", "ham",
            # Овощи
            "potatoes", "corn", "beans", "rice", "tomatoes", "lettuce", "onions",
            "bell peppers", "broccoli", "carrots", "celery",
            # Молочные
            "cheese", "milk", "butter", "yogurt", "cream",
            # Хлебобулочные
            "bread", "bagels", "muffins", "pancakes",
            # Другое
            "eggs", "olive oil", "vegetable oil", "salt", "pepper", "sugar"
        ],
        "seasonal_products": {
            "spring": ["asparagus", "strawberries", "peas", "artichokes", "spring onions"],
            "summer": ["corn", "tomatoes", "berries", "peaches", "zucchini", "cucumber"],
            "autumn": ["pumpkin", "apples", "squash", "sweet potatoes", "cranberries"],
            "winter": ["citrus", "root vegetables", "preserved foods", "winter squash"]
        },
        "cooking_methods": [
            "grilling", "frying", "baking", "roasting", "steaming", 
            "sautéing", "broiling", "smoking", "slow cooking"
        ],
        "measurement_units": "imperial",
        "dietary_preferences": ["keto", "paleo", "vegan", "gluten-free", "low-carb", "mediterranean"],
        "food_culture_notes": "Diverse American cuisine with emphasis on convenience, variety, and fusion of international flavors. Strong BBQ and comfort food traditions.",
        "region_code": "US"
    },
    
    "DE": {
        "cuisine_types": ["немецкая", "баварская", "европейская"],
        "common_products": [
            # Мясо
            "schweinefleisch", "rindfleisch", "hähnchen", "wurst", "speck",
            # Овощи
            "kartoffeln", "kohl", "zwiebeln", "karotten", "gurken",
            # Молочные
            "milch", "käse", "butter", "quark", "sahne",
            # Хлебобулочные
            "brot", "brötchen", "brezel",
            # Другое
            "eier", "öl", "salz", "pfeffer", "zucker"
        ],
        "seasonal_products": {
            "spring": ["spargel", "radieschen", "frühlingszwiebeln"],
            "summer": ["tomaten", "gurken", "beeren", "kirschen"],
            "autumn": ["kürbis", "äpfel", "pilze", "kohl"],
            "winter": ["sauerkraut", "wurzelgemüse", "konserven"]
        },
        "cooking_methods": [
            "kochen", "braten", "backen", "schmoren", "grillen", 
            "dämpfen", "einlegen", "räuchern"
        ],
        "measurement_units": "metric",
        "dietary_preferences": ["traditionell", "bio", "vegetarisch", "regional"],
        "food_culture_notes": "Traditional German cuisine emphasizing hearty meals, bread, sausages, and beer culture. Strong regional variations.",
        "region_code": "DE"
    },
    
    "FR": {
        "cuisine_types": ["французская", "провансальская", "нормандская"],
        "common_products": [
            # Мясо и птица
            "bœuf", "porc", "poulet", "canard", "agneau",
            # Овощи
            "pommes de terre", "oignons", "tomates", "courgettes", "aubergines",
            # Молочные
            "fromage", "lait", "beurre", "crème", "yaourt",
            # Хлебобулочные
            "pain", "baguette", "croissant",
            # Другое
            "œufs", "huile d'olive", "vin", "herbes"
        ],
        "seasonal_products": {
            "spring": ["asperges", "petits pois", "radis", "fraises"],
            "summer": ["tomates", "courgettes", "aubergines", "pêches"],
            "autumn": ["champignons", "pommes", "poires", "châtaignes"],
            "winter": ["choux", "poireaux", "agrumes", "conserves"]
        },
        "cooking_methods": [
            "sauté", "braisé", "rôti", "grillé", "poché", 
            "confit", "flambé", "mariné"
        ],
        "measurement_units": "metric",
        "dietary_preferences": ["traditionnel", "bio", "terroir", "gastronomique"],
        "food_culture_notes": "Refined French cuisine with emphasis on technique, quality ingredients, and regional specialties. Strong wine and cheese culture.",
        "region_code": "FR"
    },
    
    "IT": {
        "cuisine_types": ["итальянская", "средиземноморская", "региональная"],
        "common_products": [
            # Основа
            "pasta", "riso", "pomodori", "olio d'oliva", "aglio",
            # Мясо и рыба
            "manzo", "maiale", "pollo", "pesce", "prosciutto",
            # Молочные
            "formaggio", "mozzarella", "parmigiano", "ricotta",
            # Овощи
            "basilico", "origano", "cipolla", "peperoni", "melanzane",
            # Хлебобулочные
            "pane", "pizza", "focaccia"
        ],
        "seasonal_products": {
            "spring": ["carciofi", "asparagi", "piselli", "fragole"],
            "summer": ["pomodori", "zucchine", "melanzane", "pesche"],
            "autumn": ["funghi", "castagne", "uva", "zucca"],
            "winter": ["cavoli", "agrumi", "conserve", "olive"]
        },
        "cooking_methods": [
            "bollire", "friggere", "arrostire", "grigliare", "brasare",
            "saltare", "marinare", "affumicare"
        ],
        "measurement_units": "metric",
        "dietary_preferences": ["mediterranea", "tradizionale", "biologica", "regionale"],
        "food_culture_notes": "Italian cuisine focused on fresh, high-quality ingredients, regional diversity, and traditional preparation methods. Strong pasta and wine culture.",
        "region_code": "IT"
    },
    
    "JP": {
        "cuisine_types": ["японская", "азиатская"],
        "common_products": [
            # Основа
            "米", "醤油", "味噌", "だし", "海苔",
            # Рыба и морепродукты
            "魚", "エビ", "カニ", "イカ", "タコ",
            # Овощи
            "大根", "人参", "玉ねぎ", "キャベツ", "きゅうり",
            # Другое
            "豆腐", "卵", "ごま油", "酢", "砂糖"
        ],
        "seasonal_products": {
            "spring": ["たけのこ", "桜餅", "いちご", "菜の花"],
            "summer": ["きゅうり", "トマト", "なす", "すいか"],
            "autumn": ["さつまいも", "柿", "栗", "きのこ"],
            "winter": ["大根", "白菜", "みかん", "鍋料理"]
        },
        "cooking_methods": [
            "煮る", "焼く", "蒸す", "揚げる", "炒める",
            "刺身", "寿司", "漬ける", "燻製"
        ],
        "measurement_units": "metric",
        "dietary_preferences": ["和食", "健康志向", "季節料理", "精進料理"],
        "food_culture_notes": "Traditional Japanese cuisine emphasizing seasonal ingredients, umami flavors, and aesthetic presentation. Strong rice and seafood culture.",
        "region_code": "JP"
    },
    
    "AE": {
        "cuisine_types": ["эмиратская", "арабская", "ближневосточная", "международная"],
        "common_products": [
            # Мясо и птица
            "لحم الضأن", "دجاج", "لحم البقر", "جمل", "سمك", "روبيان",
            # Рис и злаки
            "أرز بسمتي", "برغل", "قمح", "شعير",
            # Овощи и фрукты
            "طماطم", "خيار", "باذنجان", "فلفل", "بصل", "ثوم", "نعناع", "بقدونس",
            "تمر", "رمان", "تين", "عنب", "مانجو",
            # Молочные и яйца
            "لبن", "جبن", "زبدة", "لبن رائب", "بيض",
            # Специи и приправы
            "هيل", "قرفة", "زعفران", "كمون", "كزبرة", "فلفل أسود", "ملح",
            # Масла и жиры
            "زيت زيتون", "سمن", "زيت نباتي",
            # Хлебобулочные
            "خبز عربي", "رقاق", "لقيمات"
        ],
        "seasonal_products": {
            "spring": ["فراولة", "خس", "جزر", "فجل", "بازلاء"],
            "summer": ["بطيخ", "شمام", "عنب", "تين", "خيار"],
            "autumn": ["تمر", "رمان", "جوز", "لوز", "تين"],
            "winter": ["برتقال", "ليمون", "جريب فروت", "خضروات ورقية"]
        },
        "cooking_methods": [
            "شوي", "قلي", "طبخ", "خبز", "تحمير",
            "طبخ بالبخار", "تتبيل", "تخليل", "تجفيف"
        ],
        "measurement_units": "metric",
        "dietary_preferences": ["حلال", "تقليدي", "صحي", "عضوي", "بدوي"],
        "food_culture_notes": "Эмиратская кухня сочетает традиционные арабские блюда с международными влияниями. Акцент на свежих морепродуктах, рисе, специях и халяльном мясе. Важную роль играют финики и традиционные методы приготовления.",
        "region_code": "AE"
    },
    
    "SA": {
        "cuisine_types": ["саудовская", "арабская", "ближневосточная", "бедуинская"],
        "common_products": [
            # Мясо и птица
            "لحم الضأن", "لحم الماعز", "دجاج", "لحم البقر", "جمل",
            # Рис и злаки
            "أرز بسمتي", "قمح", "شعير", "دخن", "ذرة",
            # Овощи
            "طماطم", "خيار", "باذنجان", "كوسا", "بصل", "ثوم", "فلفل",
            "جزر", "بطاطس", "ملوخية", "بامية",
            # Фрукты
            "تمر", "عنب", "رمان", "تين", "مشمش", "خوخ",
            # Молочные
            "لبن", "لبن رائب", "جبن", "زبدة", "قشطة",
            # Специи
            "هيل", "قرفة", "زعفران", "كمون", "كزبرة", "حلبة", "بهارات مشكلة",
            # Масла
            "زيت زيتون", "سمن بلدي", "زيت السمسم",
            # Хлебобулочные
            "خبز", "صمون", "تميس", "قرصان"
        ],
        "seasonal_products": {
            "spring": ["خس", "جرجير", "فجل", "بازلاء", "فول أخضر"],
            "summer": ["بطيخ", "شمام", "عنب", "تين", "خوخ"],
            "autumn": ["تمر", "رمان", "جوز", "لوز", "فستق"],
            "winter": ["برتقال", "يوسفي", "ليمون", "خضروات ورقية", "جزر"]
        },
        "cooking_methods": [
            "شوي", "قلي", "طبخ", "خبز في التنور", "طبخ بالفحم",
            "تحمير", "سلق", "تبخير", "تجفيف", "حفظ بالملح"
        ],
        "measurement_units": "metric",
        "dietary_preferences": ["حلال", "تقليدي", "بدوي", "صحراوي", "عضوي"],
        "food_culture_notes": "Традиционная саудовская кухня основана на бедуинских традициях с акцентом на мясо, рис, финики и молочные продукты. Важную роль играют специи, особенно кардамон и шафран. Гостеприимство и совместные трапезы - основа пищевой культуры.",
        "region_code": "SA"
    }
}


def get_regional_cuisine(country_code: str) -> Dict[str, Any]:
    """
    Получить региональную кухню по коду страны
    
    Args:
        country_code: ISO код страны
        
    Returns:
        Словарь с данными о региональной кухне
    """
    return REGIONAL_CUISINES.get(country_code.upper(), get_default_cuisine())


def get_default_cuisine() -> Dict[str, Any]:
    """
    Получить кухню по умолчанию (международная)
    
    Returns:
        Словарь с базовыми данными о кухне
    """
    return {
        "cuisine_types": ["international", "fusion"],
        "common_products": [
            "rice", "pasta", "bread", "chicken", "beef", "fish",
            "potatoes", "tomatoes", "onions", "garlic", "oil",
            "milk", "cheese", "eggs", "salt", "pepper"
        ],
        "seasonal_products": {
            "spring": ["asparagus", "peas", "strawberries"],
            "summer": ["tomatoes", "corn", "berries"],
            "autumn": ["apples", "pumpkin", "mushrooms"],
            "winter": ["citrus", "root vegetables", "preserved foods"]
        },
        "cooking_methods": [
            "boiling", "frying", "baking", "grilling", "steaming", "roasting"
        ],
        "measurement_units": "metric",
        "dietary_preferences": ["balanced", "healthy", "varied"],
        "food_culture_notes": "International cuisine with diverse cooking methods and ingredients from various culinary traditions.",
        "region_code": "INTL"
    }


def get_available_regions() -> List[str]:
    """
    Получить список доступных регионов
    
    Returns:
        Список кодов стран
    """
    return list(REGIONAL_CUISINES.keys())


def search_products_by_region(country_code: str, search_term: str) -> List[str]:
    """
    Поиск продуктов в региональной кухне
    
    Args:
        country_code: ISO код страны
        search_term: Поисковый термин
        
    Returns:
        Список найденных продуктов
    """
    cuisine = get_regional_cuisine(country_code)
    search_term = search_term.lower()
    
    found_products = []
    
    # Поиск в основных продуктах
    for product in cuisine["common_products"]:
        if search_term in product.lower():
            found_products.append(product)
    
    # Поиск в сезонных продуктах
    for season, products in cuisine["seasonal_products"].items():
        for product in products:
            if search_term in product.lower() and product not in found_products:
                found_products.append(product)
    
    return found_products


def get_seasonal_products(country_code: str, season: str = None) -> List[str]:
    """
    Получить сезонные продукты для региона
    
    Args:
        country_code: ISO код страны
        season: Сезон (spring, summer, autumn, winter) или None для текущего
        
    Returns:
        Список сезонных продуктов
    """
    cuisine = get_regional_cuisine(country_code)
    
    if season is None:
        # Определяем текущий сезон
        month = datetime.now().month
        if month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        elif month in [9, 10, 11]:
            season = "autumn"
        else:
            season = "winter"
    
    return cuisine["seasonal_products"].get(season, [])


def get_cooking_methods(country_code: str) -> List[str]:
    """
    Получить методы готовки для региона
    
    Args:
        country_code: ISO код страны
        
    Returns:
        Список методов готовки
    """
    cuisine = get_regional_cuisine(country_code)
    return cuisine["cooking_methods"]


def is_product_common_in_region(country_code: str, product: str) -> bool:
    """
    Проверить, является ли продукт распространенным в регионе
    
    Args:
        country_code: ISO код страны
        product: Название продукта
        
    Returns:
        True если продукт распространен в регионе
    """
    cuisine = get_regional_cuisine(country_code)
    product_lower = product.lower()
    
    # Проверяем в основных продуктах
    for common_product in cuisine["common_products"]:
        if product_lower in common_product.lower() or common_product.lower() in product_lower:
            return True
    
    # Проверяем в сезонных продуктах
    for season_products in cuisine["seasonal_products"].values():
        for seasonal_product in season_products:
            if product_lower in seasonal_product.lower() or seasonal_product.lower() in product_lower:
                return True
    
    return False