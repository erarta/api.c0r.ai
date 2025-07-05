import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_supabase(monkeypatch):
    # Patch supabase client methods globally
    from utils import supabase
    monkeypatch.setattr(supabase, "supabase", MagicMock())
    return supabase.supabase

@pytest.fixture
def mock_update():
    update = MagicMock()
    update.effective_user.id = 123456789
    update.message.reply_text = AsyncMock()
    update.message.photo = [MagicMock(file_id="file_1"), MagicMock(file_id="file_2")]  # Simulate two resolutions
    return update

@pytest.fixture
def mock_context():
    context = MagicMock()
    context.bot.get_file = AsyncMock()
    file_mock = MagicMock()
    file_mock.download_as_bytearray = AsyncMock(return_value=b"fakebytes")
    context.bot.get_file.return_value = file_mock
    return context 