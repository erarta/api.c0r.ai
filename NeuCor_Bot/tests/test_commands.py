import pytest
from handlers.commands import start_command, help_command

@pytest.mark.asyncio
async def test_start_command_new_user(mock_update, mock_context, mock_supabase, monkeypatch):
    # Simulate new user creation
    mock_supabase.table().select().eq().execute.return_value.data = []
    mock_supabase.table().insert().execute.return_value.data = [{
        "id": 1, "telegram_id": 123456789, "credits_remaining": 3, "total_paid": 0, "created_at": "now"
    }]
    await start_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_awaited_with("Welcome! You have been registered and received 3 free credits.")

@pytest.mark.asyncio
async def test_start_command_existing_user(mock_update, mock_context, mock_supabase, monkeypatch):
    # Simulate existing user
    mock_supabase.table().select().eq().execute.return_value.data = [{
        "id": 1, "telegram_id": 123456789, "credits_remaining": 2, "total_paid": 0, "created_at": "now"
    }]
    await start_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_awaited_with("Welcome back! You have 2 credits.")

@pytest.mark.asyncio
async def test_start_command_error(mock_update, mock_context, mock_supabase, monkeypatch):
    # Simulate Supabase error
    mock_supabase.table().select().eq().execute.side_effect = Exception("DB error")
    await start_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_awaited_with("An error occurred. Please try again later.")

@pytest.mark.asyncio
async def test_help_command(mock_update, mock_context):
    await help_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_awaited() 