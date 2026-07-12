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
        return {"api_url": DEFAULT_API_URL, "access_token": None}
    with CONFIG_FILE.open() as f:
        data = yaml.safe_load(f) or {}
    data.setdefault("api_url", DEFAULT_API_URL)
    return data


def save_config(data: dict) -> None:
    ensure_config_dir()
    with CONFIG_FILE.open("w") as f:
        yaml.safe_dump(data, f)


def get_api_url() -> str:
    return load_config().get("api_url", DEFAULT_API_URL).rstrip("/")


def get_token() -> str | None:
    return load_config().get("access_token")


def set_token(token: str) -> None:
    config = load_config()
    config["access_token"] = token
    save_config(config)


def set_api_url(url: str) -> None:
    config = load_config()
    config["api_url"] = url.rstrip("/")
    save_config(config)
