"""llm plugin for EmpirioLabs AI.

Registers the chat models in the live EmpirioLabs AI catalog
(https://api.empiriolabs.ai/v1/models) with Simon Willison's ``llm`` CLI.
"""

import json
import time
import urllib.request
from pathlib import Path

import llm
from llm.default_plugins.openai_models import Chat

# AsyncChat was added to llm later; degrade gracefully on older versions.
try:
    from llm.default_plugins.openai_models import AsyncChat

    HAS_ASYNC = True
except ImportError:  # pragma: no cover
    HAS_ASYNC = False

API_BASE = "https://api.empiriolabs.ai/v1"

# No model list lives in code: one goes stale as models are added and retired (one here named a retired model,
# 2026-10-29). The models come only from GET https://api.empiriolabs.ai/v1/models, or from its cached copy when
# that call fails; with neither, the plugin registers no models (a run could not reach the API anyway).
FALLBACK_MODELS = ()


def fetch_cached_json(url, path, cache_timeout, headers=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        mod_time = path.stat().st_mtime
        if time.time() - mod_time < cache_timeout:
            return json.loads(path.read_text())
    # The standard library, not httpx: llm 0.36 and openai 3 depend on httpx2, so
    # `import httpx` failed in a current install and only the fallback list showed.
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "llm-empiriolabs", **(headers or {})})
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        path.write_text(json.dumps(data))
        return data
    except Exception:
        # Network failure: serve the stale cache if we have one.
        if path.is_file():
            return json.loads(path.read_text())
        raise


def get_model_ids(key=None, skip_cache=False):
    """Return the EmpirioLabs model slugs, preferring the live catalog."""
    headers = {"Authorization": "Bearer {}".format(key)} if key else None
    try:
        data = fetch_cached_json(
            url="{}/models".format(API_BASE),
            path=llm.user_dir() / "empiriolabs_models.json",
            cache_timeout=0 if skip_cache else 3600,
            headers=headers,
        )
        models = data.get("data", data) if isinstance(data, dict) else data
        # Only models that answer chat completions: the catalog also lists image,
        # video, speech and other models that this plugin cannot run.
        ids = [
            m["id"]
            for m in models
            if isinstance(m, dict) and m.get("id") and "POST /v1/chat/completions" in (m.get("supported_endpoints") or [])
        ]
        if ids:
            return ids
    except Exception:
        pass
    return list(FALLBACK_MODELS)


class _EmpirioLabsChat:
    needs_key = "empiriolabs"
    key_env_var = "EMPIRIOLABS_API_KEY"

    def __init__(self, model_name):
        super().__init__(
            model_name=model_name,
            model_id="empiriolabs/{}".format(model_name),
            api_base=API_BASE,
        )

    def __str__(self):
        return "EmpirioLabs AI: {}".format(self.model_id)


class EmpirioLabsChat(_EmpirioLabsChat, Chat):
    pass


if HAS_ASYNC:

    class EmpirioLabsAsyncChat(_EmpirioLabsChat, AsyncChat):
        pass


@llm.hookimpl
def register_models(register):
    key = llm.get_key("", "empiriolabs", "EMPIRIOLABS_API_KEY")
    if not key:
        return
    for model_id in get_model_ids(key=key):
        if HAS_ASYNC:
            register(
                EmpirioLabsChat(model_id),
                EmpirioLabsAsyncChat(model_id),
            )
        else:
            register(EmpirioLabsChat(model_id))
