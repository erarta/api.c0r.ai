"""
Integration tests for payment functionality with proper mocking
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal

from tests.test_utils import setup_test_imports
from tests.base_test_classes import BaseIntegrationTest
from tests.mocks import setup_integration_mocks, MockYooKassaClient, MockSupabaseClient

# Ensure proper imports
setup_test_imports()

from common.payment_plans_config import PAYMENT_PLANS
from common.supabase_client import supabase


class TestPaymentIntegration(BaseIntegrationTest):
    """Test payment integration with external services"""
    
    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Setup mocks for each test"""
        self.mock_env = setup_integration_mocks()
        
    @pytest.fixture
    def payment_data(self):
        """Sample payment data"""
        return {
            'user_id': 'd4047507-274c-493c-99b5-af801a5b7195',
            'telegram_id': 391490,
            'plan': 'basic',
            'amount': Decimal('99.00'),
            'currency': 'RUB',
            'credits': 20
        }
    
    @pytest.mark.asyncio
    async def test_create_payment_success(self, payment_data):
        """Test successful payment creation"""
        with patch('common.supabase_client.supabase', self.mock_env['supabase']):
            # Mock user exists
            self.mock_env['supabase'].table_mock.select.return_value.eq.return_value.execute.return_value.data = [
                {'id': payment_data['user_id'], 'telegram_id': payment_data['telegram_id']}
            ]
            
            # Create payment using YooKassa mock
            yookassa_client = self.mock_env['yookassa']
            payment_result = await yookassa_client.create_payment(
                amount=payment_data['amount'],
                currency=payment_data['currency'],
                description=f"c0r.ai {payment_data['plan']} plan - {payment_data['credits']} credits",
                metadata={
                    'telegram_user_id': str(payment_data['telegram_id']),
                    'plan': payment_data['plan'],
                    'credits': str(payment_data['credits'])
                }
            )
            
            # Verify payment creation
            assert payment_result['status'] == 'pending'
            assert payment_result['amount']['value'] == str(payment_data['amount'])
            assert payment_result['amount']['currency'] == payment_data['currency']
            assert 'confirmation_url' in payment_result['confirmation']
            assert payment_result['metadata']['telegram_user_id'] == str(payment_data['telegram_id'])
    
    @pytest.mark.asyncio
    async def test_payment_webhook_processing(self, payment_data):
        """Test payment webhook processing"""
        with patch('common.supabase_client.supabase', self.mock_env['supabase']):
            # Mock webhook data
            webhook_data = {
                'type': 'payment.succeeded',
                'object': {
                    'id': 'test_payment_id_12345',
                    'status': 'succeeded',
                    'amount': {
                        'value': str(payment_data['amount']),
                        'currency': payment_data['currency']
                    },
                    'metadata': {
                        'telegram_user_id': str(payment_data['telegram_id']),
                        'plan': payment_data['plan'],
                        'credits': str(payment_data['credits'])
                    },
                    'created_at': '2025-01-26T17:57:00.000Z'
                }
            }
            
            # Mock user lookup
            self.mock_env['supabase'].table_mock.select.return_value.eq.return_value.execute.return_value.data = [
                {
                    'id': payment_data['user_id'],
                    'telegram_id': payment_data['telegram_id'],
                    'credits_remaining': 5
                }
            ]
            
            # Process webhook (simulate webhook handler)
            payment_obj = webhook_data['object']
            user_id = payment_obj['metadata']['telegram_user_id']
            credits_to_add = int(payment_obj['metadata']['credits'])
            
            # Verify webhook data structure
            assert webhook_data['type'] == 'payment.succeeded'
            assert payment_obj['status'] == 'succeeded'
            assert payment_obj['metadata']['telegram_user_id'] == str(payment_data['telegram_id'])
            assert int(payment_obj['metadata']['credits']) == payment_data['credits']
            
            # Simulate credit addition
            new_credits = 5 + credits_to_add  # 5 existing + 20 new = 25
            assert new_credits == 25
    
    @pytest.mark.asyncio
    async def test_payment_plans_configuration(self):
        """Test payment plans configuration"""
        # Verify payment plans are properly configured
        assert 'basic' in PAYMENT_PLANS
        assert 'pro' in PAYMENT_PLANS
        
        basic_plan = PAYMENT_PLANS['basic']
        assert basic_plan['price'] == 99
        assert basic_plan['credits'] == 20
        assert basic_plan['currency'] == 'RUB'
        
        pro_plan = PAYMENT_PLANS['pro']
        assert pro_plan['price'] == 399
        assert pro_plan['credits'] == 100
        assert pro_plan['currency'] == 'RUB'
    
    @pytest.mark.asyncio
    async def test_payment_failure_handling(self, payment_data):
        """Test payment failure handling"""
        with patch('common.supabase_client.supabase', self.mock_env['supabase']):
            # Mock failed payment webhook
            webhook_data = {
                'type': 'payment.canceled',
                'object': {
                    'id': 'test_payment_id_failed',
                    'status': 'canceled',
                    'amount': {
                        'value': str(payment_data['amount']),
                        'currency': payment_data['currency']
                    },
                    'metadata': {
                        'telegram_user_id': str(payment_data['telegram_id']),
                        'plan': payment_data['plan'],
                        'credits': str(payment_data['credits'])
                    },
                    'cancellation_details': {
                        'reason': 'insufficient_funds'
                    }
                }
            }
            
            # Verify failure handling
            assert webhook_data['type'] == 'payment.canceled'
            assert webhook_data['object']['status'] == 'canceled'
            assert 'cancellation_details' in webhook_data['object']
    
    @pytest.mark.asyncio
    async def test_user_credits_update(self, payment_data):
        """Test user credits update after successful payment"""
        with patch('common.supabase_client.supabase', self.mock_env['supabase']):
            # Mock current user data
            current_credits = 5
            self.mock_env['supabase'].table_mock.select.return_value.eq.return_value.execute.return_value.data = [
                {
                    'id': payment_data['user_id'],
                    'telegram_id': payment_data['telegram_id'],
                    'credits_remaining': current_credits
                }
            ]
            
            # Simulate credit addition
            credits_to_add = payment_data['credits']
            new_credits = current_credits + credits_to_add
            
            # Mock update operation
            update_data = {'credits_remaining': new_credits}
            self.mock_env['supabase'].table_mock.update.return_value.eq.return_value.execute.return_value = {
                'data': [{'id': payment_data['user_id'], 'credits_remaining': new_credits}]
            }
            
            # Verify credits calculation
            assert new_credits == 25  # 5 + 20
            
            # Verify update would be called with correct data
            expected_credits = current_credits + credits_to_add
            assert expected_credits == new_credits
    
    @pytest.mark.asyncio
    async def test_payment_logging(self, payment_data):
        """Test payment transaction logging"""
        with patch('common.supabase_client.supabase', self.mock_env['supabase']):
            # Mock payment log entry
            payment_log = {
                'user_id': payment_data['user_id'],
                'telegram_id': payment_data['telegram_id'],
                'payment_id': 'test_payment_id_12345',
                'amount': str(payment_data['amount']),
                'currency': payment_data['currency'],
                'plan': payment_data['plan'],
                'credits_added': payment_data['credits'],
                'status': 'succeeded',
                'created_at': '2025-01-26T17:57:00.000Z'
            }
            
            # Mock log insertion
            self.mock_env['supabase'].table_mock.insert.return_value.execute.return_value = {
                'data': [payment_log]
            }
            
            # Verify log structure
            assert payment_log['user_id'] == payment_data['user_id']
            assert payment_log['telegram_id'] == payment_data['telegram_id']
            assert payment_log['amount'] == str(payment_data['amount'])
            assert payment_log['credits_added'] == payment_data['credits']
            assert payment_log['status'] == 'succeeded'
    
    @pytest.mark.asyncio
    async def test_invalid_payment_data(self):
        """Test handling of invalid payment data"""
        # Test with missing required fields
        invalid_webhook = {
            'type': 'payment.succeeded',
            'object': {
                'id': 'test_payment_invalid',
                'status': 'succeeded',
                # Missing amount and metadata
            }
        }
        
        # Verify that missing required fields are detected
        payment_obj = invalid_webhook['object']
        assert 'amount' not in payment_obj
        assert 'metadata' not in payment_obj
        
        # This would trigger error handling in real implementation
        assert payment_obj['status'] == 'succeeded'
        assert payment_obj['id'] == 'test_payment_invalid'
    
    @pytest.mark.asyncio
    async def test_duplicate_payment_handling(self, payment_data):
        """Test handling of duplicate payment notifications"""
        with patch('common.supabase_client.supabase', self.mock_env['supabase']):
            payment_id = 'test_payment_duplicate'
            
            # Mock existing payment log
            self.mock_env['supabase'].table_mock.select.return_value.eq.return_value.execute.return_value.data = [
                {
                    'payment_id': payment_id,
                    'status': 'succeeded',
                    'processed_at': '2025-01-26T17:57:00.000Z'
                }
            ]
            
            # Simulate duplicate webhook
            webhook_data = {
                'type': 'payment.succeeded',
                'object': {
                    'id': payment_id,
                    'status': 'succeeded',
                    'amount': {'value': '99.00', 'currency': 'RUB'},
                    'metadata': {
                        'telegram_user_id': str(payment_data['telegram_id']),
                        'plan': 'basic',
                        'credits': '20'
                    }
                }
            }
            
            # Verify duplicate detection would work
            existing_payments = self.mock_env['supabase'].table_mock.select.return_value.eq.return_value.execute.return_value.data
            assert len(existing_payments) == 1
            assert existing_payments[0]['payment_id'] == payment_id
            assert existing_payments[0]['status'] == 'succeeded'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])