from app.config import get_settings


def test_settings_load():
    settings = get_settings()
    assert settings.database_url.startswith("sqlite")
