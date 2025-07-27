"""
Mock modules for testing external services
"""
from .external_services import (
    MockSupabaseClient,
    MockYooKassaClient,
    MockMLServiceClient,
    MockTelegramBot,
    MockR2Storage,
    create_mock_environment,
    setup_integration_mocks
)

__all__ = [
    'MockSupabaseClient',
    'MockYooKassaClient', 
    'MockMLServiceClient',
    'MockTelegramBot',
    'MockR2Storage',
    'create_mock_environment',
    'setup_integration_mocks'
]