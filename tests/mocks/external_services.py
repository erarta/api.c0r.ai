"""
Mock external services for integration tests
"""
from unittest.mock import AsyncMock, MagicMock
from tests.test_utils import setup_test_imports

# Ensure proper imports
setup_test_imports()


class MockSupabaseClient:
    """Mock Supabase client for integration tests"""
    
    def __init__(self):
        self.table_mock = MagicMock()
        self.table_mock.select.return_value.eq.return_value.execute.return_value.data = []
        
    def table(self, table_name):
        """Mock table method"""
        return self.table_mock
    
    def from_(self, table_name):
        """Mock from_ method"""
        return self.table_mock


class MockYooKassaClient:
    """Mock YooKassa client for payment tests"""
    
    def __init__(self):
        self.payment = MagicMock()
    
    async def create_payment(self, amount, currency, description, **kwargs):
        """Mock payment creation"""
        return {
            'id': 'test_payment_id_12345',
            'status': 'pending',
            'amount': {'value': str(amount), 'currency': currency},
            'description': description,
            'confirmation': {
                'type': 'redirect',
                'confirmation_url': 'https://test.yookassa.ru/payments/test_payment_id_12345'
            },
            'created_at': '2025-01-26T17:57:00.000Z',
            'metadata': kwargs.get('metadata', {})
        }
    
    async def find_one(self, payment_id):
        """Mock payment retrieval"""
        return {
            'id': payment_id,
            'status': 'succeeded',
            'amount': {'value': '100.00', 'currency': 'RUB'},
            'description': 'Test payment',
            'paid': True,
            'created_at': '2025-01-26T17:57:00.000Z'
        }


class MockMLServiceClient:
    """Mock ML service client for nutrition analysis"""
    
    def __init__(self):
        self.base_url = "http://localhost:8001"
    
    async def analyze_nutrition(self, image_url, user_preferences=None):
        """Mock nutrition analysis"""
        return {
            "success": True,
            "kbzhu": {
                "calories": 450,
                "proteins": 25.0,
                "fats": 15.0,
                "carbohydrates": 45.0
            },
            "food_items": [
                {
                    "name": "Куриная грудка",
                    "weight": "150г",
                    "calories": 250,
                    "proteins": 23.0,
                    "fats": 2.0,
                    "carbohydrates": 0.0
                },
                {
                    "name": "Рис отварной",
                    "weight": "100г",
                    "calories": 200,
                    "proteins": 2.0,
                    "fats": 13.0,
                    "carbohydrates": 45.0
                }
            ],
            "confidence": 0.95,
            "processing_time": 1.2
        }
    
    async def generate_recipe(self, image_url, dietary_preferences=None, allergies=None):
        """Mock recipe generation"""
        return {
            "success": True,
            "recipe": {
                "name": "Куриная грудка с рисом",
                "description": "Полезное блюдо с высоким содержанием белка",
                "ingredients": [
                    "Куриная грудка - 150г",
                    "Рис - 100г",
                    "Оливковое масло - 1 ст.л.",
                    "Соль, перец - по вкусу"
                ],
                "instructions": [
                    "1. Разогрейте сковороду с оливковым маслом",
                    "2. Обжарьте куриную грудку до золотистой корочки",
                    "3. Отварите рис согласно инструкции на упаковке",
                    "4. Подавайте курицу с рисом"
                ],
                "nutrition": {
                    "calories": 450,
                    "proteins": 25.0,
                    "fats": 15.0,
                    "carbohydrates": 45.0
                },
                "cooking_time": 30,
                "difficulty": "easy"
            },
            "confidence": 0.92,
            "processing_time": 2.1
        }


class MockTelegramBot:
    """Mock Telegram bot for integration tests"""
    
    def __init__(self):
        self.id = 12345
        self.username = "test_bot"
        self.get_file = AsyncMock()
        self.download_file = AsyncMock()
        self.send_message = AsyncMock()
        self.edit_message_text = AsyncMock()
        self.answer_callback_query = AsyncMock()
        
        # Mock file operations
        self.get_file.return_value.file_path = "test/path/photo.jpg"
        self.download_file.return_value = b"fake_image_data"
    
    async def get_me(self):
        """Mock get_me method"""
        return {
            'id': self.id,
            'is_bot': True,
            'first_name': 'Test Bot',
            'username': self.username,
            'can_join_groups': True,
            'can_read_all_group_messages': False,
            'supports_inline_queries': False
        }


class MockR2Storage:
    """Mock Cloudflare R2 storage for file uploads"""
    
    def __init__(self):
        self.uploaded_files = {}
    
    async def upload_file(self, file_data, filename, content_type="image/jpeg"):
        """Mock file upload"""
        file_url = f"https://test-r2.example.com/{filename}"
        self.uploaded_files[filename] = {
            'url': file_url,
            'size': len(file_data),
            'content_type': content_type,
            'uploaded_at': '2025-01-26T17:57:00.000Z'
        }
        return file_url
    
    async def delete_file(self, filename):
        """Mock file deletion"""
        if filename in self.uploaded_files:
            del self.uploaded_files[filename]
            return True
        return False
    
    def get_signed_url(self, filename, expires_in=3600):
        """Mock signed URL generation"""
        if filename in self.uploaded_files:
            return f"https://test-r2.example.com/{filename}?signed=true&expires={expires_in}"
        return None


def create_mock_environment():
    """Create a complete mock environment for integration tests"""
    return {
        'supabase': MockSupabaseClient(),
        'yookassa': MockYooKassaClient(),
        'ml_service': MockMLServiceClient(),
        'telegram_bot': MockTelegramBot(),
        'r2_storage': MockR2Storage()
    }


def setup_integration_mocks():
    """Setup common mocks for integration tests"""
    import os
    
    # Set test environment variables
    os.environ.update({
        'ENVIRONMENT': 'test',
        'SUPABASE_URL': 'http://localhost:54321',
        'SUPABASE_SERVICE_ROLE_KEY': 'test_key',
        'YOOKASSA_SHOP_ID': 'test_shop_id',
        'YOOKASSA_SECRET_KEY': 'test_secret_key',
        'ML_SERVICE_URL': 'http://localhost:8001',
        'TELEGRAM_BOT_TOKEN': 'test_token',
        'R2_BUCKET_NAME': 'test-bucket',
        'R2_ACCESS_KEY_ID': 'test_access_key',
        'R2_SECRET_ACCESS_KEY': 'test_secret_key'
    })
    
    return create_mock_environment()