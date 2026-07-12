from pathlib import Path

import yaml

CONFIG_DIR = Path.home() / ".scaleplane"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

DEFAULT_API_URL = "http://127.0.0.1:8000/api/v1"


def ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    ensure_config_dir()
    if not CONFIG_FILE.exists():
        return {
            "api_url": DEFAULT_API_URL,
            "access_token": None,
            "refresh_token": None,
            "organization_id": None,
        }
    with CONFIG_FILE.open() as f:
        data = yaml.safe_load(f) or {}
    data.setdefault("api_url", DEFAULT_API_URL)
    data.setdefault("access_token", None)
    data.setdefault("refresh_token", None)
    data.setdefault("organization_id", None)
    return data


def save_config(data: dict) -> None:
    ensure_config_dir()
    with CONFIG_FILE.open("w") as f:
        yaml.safe_dump(data, f)


def get_api_url() -> str:
    return load_config().get("api_url", DEFAULT_API_URL).rstrip("/")


def get_token() -> str | None:
    return load_config().get("access_token")


def get_refresh_token() -> str | None:
    return load_config().get("refresh_token")


def get_organization_id() -> str | None:
    return load_config().get("organization_id")


def set_token(token: str) -> None:
    config = load_config()
    config["access_token"] = token
    save_config(config)


def set_tokens(access: str, refresh: str, organization_id: str | None = None) -> None:
    config = load_config()
    config["access_token"] = access
    config["refresh_token"] = refresh
    config["organization_id"] = organization_id
    save_config(config)


def clear_auth() -> None:
    config = load_config()
    config["access_token"] = None
    config["refresh_token"] = None
    config["organization_id"] = None
    save_config(config)


def set_api_url(url: str) -> None:
    config = load_config()
    config["api_url"] = url.rstrip("/")
    save_config(config)
