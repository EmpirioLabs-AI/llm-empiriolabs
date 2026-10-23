"""Unit tests for the llm-empiriolabs plugin (no network required)."""

import io
import json
import urllib.error

import llm

import llm_empiriolabs


def test_api_base_constant():
    assert llm_empiriolabs.API_BASE == "https://api.empiriolabs.ai/v1"


def test_fallback_models_are_real_slugs():
    # These must match the EmpirioLabs catalog.
    expected = {
        "qwen3-7-plus",
        "qwen3-7-max",
        "deepseek-v4-pro",
        "deepseek-v4-1-flash",
        "glm-5-1",
        "kimi-k2-7-code",
        "minimax-m3",
    }
    assert set(llm_empiriolabs.FALLBACK_MODELS) == expected


def test_chat_class_config():
    model = llm_empiriolabs.EmpirioLabsChat("qwen3-7-plus")
    assert model.needs_key == "empiriolabs"
    assert model.key_env_var == "EMPIRIOLABS_API_KEY"
    assert model.api_base == "https://api.empiriolabs.ai/v1"
    assert model.model_id == "empiriolabs/qwen3-7-plus"
    assert str(model) == "EmpirioLabs AI: empiriolabs/qwen3-7-plus"


def test_get_model_ids_falls_back_when_the_catalog_is_unreachable(monkeypatch, tmp_path):
    monkeypatch.setattr(llm, "user_dir", lambda: tmp_path)

    def refuse(*args, **kwargs):
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(llm_empiriolabs.urllib.request, "urlopen", refuse)
    ids = llm_empiriolabs.get_model_ids(key=None, skip_cache=True)
    assert ids == list(llm_empiriolabs.FALLBACK_MODELS)


def test_get_model_ids_reads_chat_models_from_the_live_catalog(monkeypatch, tmp_path):
    monkeypatch.setattr(llm, "user_dir", lambda: tmp_path)
    catalog = {"data": [
        {"id": "qwen3-8-flash", "supported_endpoints": ["POST /v1/chat/completions", "POST /v1/responses"]},
        {"id": "flux-2-klein-4b", "supported_endpoints": ["POST /v1/images/generations"]},
        {"id": "glm-5-3", "supported_endpoints": ["POST /v1/chat/completions"]},
    ]}

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr(llm_empiriolabs.urllib.request, "urlopen",
                        lambda request, timeout=30: Response(json.dumps(catalog).encode()))
    assert llm_empiriolabs.get_model_ids(key="sk-test", skip_cache=True) == ["qwen3-8-flash", "glm-5-3"]


def test_plugin_is_discoverable_by_llm():
    # The entry point registers the module; llm should see our model after a key
    # is set. Here we just confirm the hook is importable and callable.
    assert hasattr(llm_empiriolabs, "register_models")
    assert callable(llm_empiriolabs.register_models)
    # llm itself imports cleanly alongside the plugin.
    assert hasattr(llm, "get_key")
