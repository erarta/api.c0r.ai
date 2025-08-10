import asyncio
import types
from importlib import reload


def async_fn(result):
    async def _inner(image_bytes, user_language, use_premium_model):
        return {"analysis": {"ok": True, "provider_called": result}}
    return _inner


def test_provider_override(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")

    from services.ml.core.providers import llm_factory as mod
    reload(mod)

    factory = mod.LLMProviderFactory()

    # Override providers with stubs
    factory.providers = {
        mod.LLMProvider.OPENAI: async_fn("openai"),
        mod.LLMProvider.PERPLEXITY: async_fn("perplexity"),
        mod.LLMProvider.GEMINI: async_fn("gemini"),
    }

    async def run():
        res = await factory.analyze_food(b"img", user_language="en", provider_override="perplexity")
        assert res["analysis"]["ok"] is True
        # llm_provider is added by factory after call
        assert res["analysis"]["llm_provider"] == "perplexity"
        assert res["analysis"]["provider_called"] == "perplexity"
    asyncio.run(run())
