import pytest
from handlers.photo import photo_handler
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_photo_handler_success(mock_update, mock_context, mock_supabase, monkeypatch):
    # User has credits
    mock_supabase.table().select().eq().execute.return_value.data = [{"credits_remaining": 2}]
    mock_supabase.table().update().eq().execute.return_value.data = [{"credits_remaining": 1}]
    # Patch get_or_create_user and decrement_credits
    monkeypatch.setattr("utils.supabase.get_or_create_user", AsyncMock(return_value=({"credits_remaining": 2}, False)))
    monkeypatch.setattr("utils.supabase.decrement_credits", AsyncMock(return_value={"credits_remaining": 1}))
    # Patch httpx.AsyncClient.post
    with patch("handlers.photo.httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json.return_value = {"kbzhu": {"calories": 100, "protein": 10, "fats": 5, "carbs": 20}}
        mock_post.return_value.raise_for_status.return_value = None
        await photo_handler(mock_update, mock_context)
    mock_update.message.reply_text.assert_any_await("Analyzing your photo, please wait... ⏳")
    assert any("Calories: 100" in str(call.args[0]) for call in mock_update.message.reply_text.await_args_list)

@pytest.mark.asyncio
async def test_photo_handler_out_of_credits(mock_update, mock_context, mock_supabase, monkeypatch):
    # User has 0 credits
    monkeypatch.setattr("utils.supabase.get_or_create_user", AsyncMock(return_value=({"credits_remaining": 0}, False)))
    await photo_handler(mock_update, mock_context)
    mock_update.message.reply_text.assert_awaited_with(
        "You are out of credits! Please buy more to continue.",
        reply_markup=pytest.helpers.anything()
    )

@pytest.mark.asyncio
async def test_photo_handler_api_error(mock_update, mock_context, mock_supabase, monkeypatch):
    # User has credits
    monkeypatch.setattr("utils.supabase.get_or_create_user", AsyncMock(return_value=({"credits_remaining": 2}, False)))
    monkeypatch.setattr("utils.supabase.decrement_credits", AsyncMock(return_value={"credits_remaining": 1}))
    with patch("handlers.photo.httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = Exception("API error")
        await photo_handler(mock_update, mock_context)
    assert any("error" in str(call.args[0]).lower() for call in mock_update.message.reply_text.await_args_list)

@pytest.mark.asyncio
async def test_photo_handler_generic_error(mock_update, mock_context, mock_supabase, monkeypatch):
    # Simulate error in get_or_create_user
    monkeypatch.setattr("utils.supabase.get_or_create_user", AsyncMock(side_effect=Exception("fail")))
    await photo_handler(mock_update, mock_context)
    assert any("error" in str(call.args[0]).lower() for call in mock_update.message.reply_text.await_args_list) 