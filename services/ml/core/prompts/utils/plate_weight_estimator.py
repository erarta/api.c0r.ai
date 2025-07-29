"""
Plate Weight Estimation Utilities for c0r.AI ML Service
Provides regional context for portion size estimation
"""

from typing import Dict, List, Optional, Tuple
from loguru import logger


class PlateWeightEstimator:
    """Утилиты для оценки веса порций с учетом региональных особенностей"""
    
    def __init__(self):
        self.regional_portion_data = self._load_regional_portion_data()
        self.plate_size_standards = self._load_plate_size_standards()
        self.density_coefficients = self._load_density_coefficients()
        
        logger.info("⚖️ PlateWeightEstimator initialized")
    
    def get_portion_context(self, region_code: str) -> str:
        """
        Получение контекста для оценки порций в регионе
        
        Args:
            region_code: Код региона (RU, US, DE, FR, IT, JP)
            
        Returns:
            Контекстная информация для оценки веса
        """
        logger.debug(f"📏 Getting portion context for {region_code}")
        
        regional_data = self.regional_portion_data.get(region_code, {})
        
        if not regional_data:
            logger.warning(f"No portion data for region {region_code}, using default")
            regional_data = self.regional_portion_data.get("DEFAULT", {})
        
        context_parts = []
        
        # Стандартные размеры тарелок
        plate_info = regional_data.get("plate_sizes", {})
        if plate_info:
            context_parts.append(f"(стандартная тарелка {plate_info.get('dinner', '25-27')} см)")
        
        # Типичные порции
        portions = regional_data.get("typical_portions", {})
        if portions:
            portion_examples = []
            for food_type, weight_range in portions.items():
                portion_examples.append(f"{food_type}: {weight_range}г")
            
            if portion_examples:
                context_parts.append(f"типичные порции: {', '.join(portion_examples[:3])}")
        
        # Культурные особенности порций
        cultural_notes = regional_data.get("cultural_notes", "")
        if cultural_notes:
            context_parts.append(cultural_notes)
        
        return " - " + ", ".join(context_parts) if context_parts else ""
    
    def estimate_food_weight(self, 
                           food_name: str, 
                           visual_size: str,
                           region_code: str = "RU") -> Tuple[int, float]:
        """
        Оценка веса продукта на основе визуального размера
        
        Args:
            food_name: Название продукта
            visual_size: Визуальный размер (small, medium, large, extra_large)
            region_code: Код региона
            
        Returns:
            Tuple[estimated_weight, confidence_score]
        """
        logger.debug(f"⚖️ Estimating weight for {food_name}, size={visual_size}, region={region_code}")
        
        # Получаем базовые веса для продукта
        base_weights = self._get_base_food_weights(food_name)
        
        # Получаем региональные коэффициенты
        regional_data = self.regional_portion_data.get(region_code, {})
        portion_multiplier = regional_data.get("portion_multiplier", 1.0)
        
        # Коэффициенты размера
        size_multipliers = {
            "tiny": 0.3,
            "small": 0.6,
            "medium": 1.0,
            "large": 1.5,
            "extra_large": 2.2,
            "huge": 3.0
        }
        
        size_multiplier = size_multipliers.get(visual_size, 1.0)
        
        # Рассчитываем итоговый вес
        base_weight = base_weights.get("medium", 100)  # Базовый вес для среднего размера
        estimated_weight = int(base_weight * size_multiplier * portion_multiplier)
        
        # Рассчитываем уверенность
        confidence = self._calculate_weight_confidence(food_name, visual_size, region_code)
        
        logger.debug(f"📊 Estimated weight: {estimated_weight}g, confidence: {confidence:.2f}")
        
        return estimated_weight, confidence
    
    def get_plate_size_reference(self, region_code: str) -> Dict[str, str]:
        """
        Получение справочной информации о размерах тарелок
        
        Args:
            region_code: Код региона
            
        Returns:
            Словарь с размерами тарелок
        """
        plate_data = self.plate_size_standards.get(region_code, {})
        
        if not plate_data:
            plate_data = self.plate_size_standards.get("DEFAULT", {})
        
        return plate_data
    
    def get_density_coefficient(self, food_category: str) -> float:
        """
        Получение коэффициента плотности для категории продуктов
        
        Args:
            food_category: Категория продукта
            
        Returns:
            Коэффициент плотности
        """
        return self.density_coefficients.get(food_category, 1.0)
    
    def _get_base_food_weights(self, food_name: str) -> Dict[str, int]:
        """Получение базовых весов для продукта"""
        
        # Нормализуем название продукта
        food_lower = food_name.lower()
        
        # Базовая база данных весов продуктов (в граммах для среднего размера)
        food_weights = {
            # Мясо и птица
            "курица": {"small": 80, "medium": 120, "large": 180},
            "говядина": {"small": 90, "medium": 140, "large": 200},
            "свинина": {"small": 85, "medium": 130, "large": 190},
            "рыба": {"small": 70, "medium": 110, "large": 160},
            "котлета": {"small": 60, "medium": 90, "large": 130},
            
            # Гарниры
            "рис": {"small": 60, "medium": 100, "large": 150},
            "картофель": {"small": 80, "medium": 120, "large": 180},
            "макароны": {"small": 70, "medium": 110, "large": 160},
            "гречка": {"small": 65, "medium": 100, "large": 140},
            "пюре": {"small": 80, "medium": 120, "large": 180},
            
            # Овощи
            "салат": {"small": 50, "medium": 80, "large": 120},
            "помидор": {"small": 60, "medium": 100, "large": 150},
            "огурец": {"small": 40, "medium": 70, "large": 100},
            "капуста": {"small": 50, "medium": 80, "large": 120},
            "морковь": {"small": 30, "medium": 50, "large": 80},
            
            # Молочные продукты
            "творог": {"small": 60, "medium": 100, "large": 150},
            "сыр": {"small": 20, "medium": 40, "large": 60},
            "йогурт": {"small": 80, "medium": 125, "large": 200},
            
            # Хлебобулочные
            "хлеб": {"small": 15, "medium": 25, "large": 40},
            "булочка": {"small": 30, "medium": 50, "large": 80},
            
            # Супы
            "суп": {"small": 150, "medium": 250, "large": 350},
            "борщ": {"small": 150, "medium": 250, "large": 350},
            
            # Каши
            "каша": {"small": 80, "medium": 120, "large": 180},
            "овсянка": {"small": 70, "medium": 110, "large": 160},
            
            # Фрукты
            "яблоко": {"small": 80, "medium": 120, "large": 180},
            "банан": {"small": 60, "medium": 100, "large": 140},
            "апельсин": {"small": 80, "medium": 130, "large": 200},
        }
        
        # Поиск по ключевым словам
        for key, weights in food_weights.items():
            if key in food_lower or food_lower in key:
                return weights
        
        # Определение по категориям
        if any(word in food_lower for word in ["мясо", "курица", "говядина", "свинина", "баранина"]):
            return {"small": 85, "medium": 130, "large": 190}
        elif any(word in food_lower for word in ["рыба", "лосось", "треска", "судак"]):
            return {"small": 70, "medium": 110, "large": 160}
        elif any(word in food_lower for word in ["овощи", "салат", "капуста", "морковь"]):
            return {"small": 45, "medium": 75, "large": 110}
        elif any(word in food_lower for word in ["каша", "рис", "гречка", "овсянка"]):
            return {"small": 70, "medium": 110, "large": 160}
        elif any(word in food_lower for word in ["суп", "борщ", "солянка", "щи"]):
            return {"small": 150, "medium": 250, "large": 350}
        
        # Базовый вес по умолчанию
        return {"small": 60, "medium": 100, "large": 150}
    
    def _calculate_weight_confidence(self, 
                                   food_name: str, 
                                   visual_size: str, 
                                   region_code: str) -> float:
        """Расчет уверенности в оценке веса"""
        
        confidence = 0.7  # Базовая уверенность
        
        # Увеличиваем уверенность для знакомых продуктов
        common_foods = ["курица", "рис", "картофель", "мясо", "рыба", "салат", "суп"]
        if any(food in food_name.lower() for food in common_foods):
            confidence += 0.1
        
        # Уверенность зависит от размера
        size_confidence = {
            "tiny": 0.6,
            "small": 0.75,
            "medium": 0.85,
            "large": 0.8,
            "extra_large": 0.7,
            "huge": 0.6
        }
        
        size_conf = size_confidence.get(visual_size, 0.7)
        confidence = (confidence + size_conf) / 2
        
        # Региональная корректировка
        if region_code in ["RU", "US", "DE"]:  # Хорошо изученные регионы
            confidence += 0.05
        
        return min(confidence, 0.95)  # Максимум 95% уверенности
    
    def _load_regional_portion_data(self) -> Dict[str, Dict]:
        """Загрузка данных о региональных порциях"""
        return {
            "RU": {
                "portion_multiplier": 1.1,  # Русские порции чуть больше среднего
                "plate_sizes": {
                    "dinner": "24-26",
                    "soup": "20-22",
                    "dessert": "18-20"
                },
                "typical_portions": {
                    "мясо": "120-150",
                    "гарнир": "100-130",
                    "салат": "70-100",
                    "суп": "250-300"
                },
                "cultural_notes": "в России принято подавать сытные порции"
            },
            "US": {
                "portion_multiplier": 1.3,  # Американские порции больше
                "plate_sizes": {
                    "dinner": "26-28",
                    "soup": "22-24",
                    "dessert": "20-22"
                },
                "typical_portions": {
                    "meat": "150-200",
                    "side": "120-160",
                    "salad": "80-120",
                    "soup": "300-400"
                },
                "cultural_notes": "американские порции традиционно большие"
            },
            "DE": {
                "portion_multiplier": 1.0,  # Немецкие порции стандартные
                "plate_sizes": {
                    "dinner": "24-26",
                    "soup": "20-22",
                    "dessert": "18-20"
                },
                "typical_portions": {
                    "fleisch": "120-140",
                    "beilage": "100-120",
                    "salat": "60-90",
                    "suppe": "250-300"
                },
                "cultural_notes": "немецкие порции умеренные и сбалансированные"
            },
            "FR": {
                "portion_multiplier": 0.9,  # Французские порции меньше
                "plate_sizes": {
                    "dinner": "22-24",
                    "soup": "18-20",
                    "dessert": "16-18"
                },
                "typical_portions": {
                    "viande": "100-120",
                    "accompagnement": "80-100",
                    "salade": "50-80",
                    "soupe": "200-250"
                },
                "cultural_notes": "французская кухня ценит качество над количеством"
            },
            "IT": {
                "portion_multiplier": 0.95,  # Итальянские порции чуть меньше среднего
                "plate_sizes": {
                    "dinner": "23-25",
                    "soup": "19-21",
                    "dessert": "17-19"
                },
                "typical_portions": {
                    "carne": "110-130",
                    "contorno": "90-110",
                    "insalata": "60-90",
                    "zuppa": "220-280"
                },
                "cultural_notes": "итальянские порции умеренные, акцент на свежести"
            },
            "JP": {
                "portion_multiplier": 0.8,  # Японские порции меньше
                "plate_sizes": {
                    "dinner": "20-22",
                    "soup": "16-18",
                    "dessert": "14-16"
                },
                "typical_portions": {
                    "肉": "80-100",
                    "ご飯": "80-120",
                    "野菜": "50-70",
                    "スープ": "150-200"
                },
                "cultural_notes": "японские порции небольшие, но разнообразные"
            },
            "DEFAULT": {
                "portion_multiplier": 1.0,
                "plate_sizes": {
                    "dinner": "24-26",
                    "soup": "20-22",
                    "dessert": "18-20"
                },
                "typical_portions": {
                    "protein": "120-150",
                    "carbs": "100-130",
                    "vegetables": "70-100"
                },
                "cultural_notes": "стандартные международные порции"
            }
        }
    
    def _load_plate_size_standards(self) -> Dict[str, Dict[str, str]]:
        """Загрузка стандартов размеров тарелок"""
        return {
            "RU": {
                "dinner_plate": "24-26 см",
                "soup_bowl": "20-22 см",
                "dessert_plate": "18-20 см",
                "bread_plate": "15-17 см"
            },
            "US": {
                "dinner_plate": "26-28 см (10-11 дюймов)",
                "soup_bowl": "22-24 см (8.5-9.5 дюймов)",
                "dessert_plate": "20-22 см (8-8.5 дюймов)",
                "bread_plate": "16-18 см (6-7 дюймов)"
            },
            "DEFAULT": {
                "dinner_plate": "24-26 см",
                "soup_bowl": "20-22 см",
                "dessert_plate": "18-20 см",
                "bread_plate": "15-17 см"
            }
        }
    
    def _load_density_coefficients(self) -> Dict[str, float]:
        """Загрузка коэффициентов плотности продуктов"""
        return {
            "liquid": 1.0,      # Жидкости (супы, напитки)
            "soft": 0.7,        # Мягкие продукты (пюре, каши)
            "medium": 0.8,      # Средней плотности (мясо, рыба)
            "dense": 1.2,       # Плотные продукты (хлеб, сыр)
            "airy": 0.3,        # Воздушные продукты (салаты, зелень)
            "granular": 0.6     # Сыпучие продукты (рис, крупы)
        }