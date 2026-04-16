import os
from typing import Any, Dict, List


DEFAULT_LANGFUSE_BASE_URL = "https://cloud.langfuse.com"


def get_langfuse_base_url() -> str:
    return (
        os.getenv("LANGFUSE_BASE_URL")
        or os.getenv("LANGFUSE_HOST")
        or DEFAULT_LANGFUSE_BASE_URL
    )


def is_langfuse_configured() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))


def get_langfuse_callbacks() -> List[Any]:
    if not is_langfuse_configured():
        return []

    base_url = get_langfuse_base_url()
    os.environ.setdefault("LANGFUSE_BASE_URL", base_url)
    os.environ.setdefault("LANGFUSE_HOST", base_url)

    try:
        from langfuse.langchain import CallbackHandler
    except ImportError:
        return []

    return [CallbackHandler()]


def is_langfuse_callback_available() -> bool:
    try:
        from langfuse.langchain import CallbackHandler  # noqa: F401
    except ImportError:
        return False

    return True


def flush_langfuse() -> None:
    if not is_langfuse_configured():
        return

    try:
        from langfuse import get_client
    except ImportError:
        return

    client = get_client()
    flush = getattr(client, "flush", None)
    if callable(flush):
        flush()


def is_langfuse_authenticated() -> bool:
    if not is_langfuse_configured():
        return False

    base_url = get_langfuse_base_url()
    os.environ.setdefault("LANGFUSE_BASE_URL", base_url)
    os.environ.setdefault("LANGFUSE_HOST", base_url)

    try:
        from langfuse import get_client
    except ImportError:
        return False

    client = get_client()
    auth_check = getattr(client, "auth_check", None)
    if not callable(auth_check):
        return False

    try:
        return bool(auth_check())
    except Exception:
        return False


def get_langfuse_status() -> Dict[str, Any]:
    try:
        import langfuse  # noqa: F401

        installed = True
    except ImportError:
        installed = False

    configured = is_langfuse_configured()
    callback_available = is_langfuse_callback_available()
    authenticated = is_langfuse_authenticated()
    return {
        "installed": installed,
        "configured": configured,
        "callback_available": callback_available,
        "authenticated": authenticated,
        "enabled": installed and configured and callback_available and authenticated,
        "base_url": get_langfuse_base_url(),
        "message": (
            "Langfuse tracing is enabled."
            if installed and configured and callback_available and authenticated
            else "Install langfuse, set LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY, and make sure the keys match this Langfuse project."
        ),
    }
