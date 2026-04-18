from __future__ import annotations

from pathlib import Path

import pytest

from avito import AvitoClient
from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core.exceptions import ConfigurationError

ENV_KEYS = (
    "AVITO_BASE_URL",
    "BASE_URL",
    "AVITO_USER_ID",
    "USER_ID",
    "AVITO_AUTH__CLIENT_ID",
    "AVITO_AUTH__CLIENT_SECRET",
    "AVITO_AUTH__REFRESH_TOKEN",
    "AVITO_CLIENT_ID",
    "AVITO_CLIENT_SECRET",
    "AVITO_SECRET",
    "CLIENT_ID",
    "CLIENT_SECRET",
    "SECRET",
)


def clear_avito_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def write_env_file(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_avito_settings_from_env_reads_full_configuration(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    clear_avito_env(monkeypatch)
    env_file = write_env_file(
        tmp_path / ".env",
        "\n".join(
            (
                "AVITO_BASE_URL=https://sandbox.avito.ru",
                "AVITO_USER_ID=42",
                "AVITO_AUTH__CLIENT_ID=client-id",
                "AVITO_AUTH__CLIENT_SECRET=client-secret",
                "AVITO_AUTH__REFRESH_TOKEN=refresh-token",
            )
        ),
    )

    settings = AvitoSettings.from_env(env_file=env_file)

    assert settings.base_url == "https://sandbox.avito.ru"
    assert settings.user_id == 42
    assert settings.auth.client_id == "client-id"
    assert settings.auth.client_secret == "client-secret"
    assert settings.auth.refresh_token == "refresh-token"


def test_avito_settings_from_env_supports_alias_variables(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    clear_avito_env(monkeypatch)
    env_file = write_env_file(
        tmp_path / ".env",
        "\n".join(
            (
                "BASE_URL=https://file.avito.ru",
                "USER_ID=77",
                "CLIENT_ID=file-client-id",
                "SECRET=file-client-secret",
            )
        ),
    )

    settings = AvitoSettings.from_env(env_file=env_file)

    assert settings.base_url == "https://file.avito.ru"
    assert settings.user_id == 77
    assert settings.auth.client_id == "file-client-id"
    assert settings.auth.client_secret == "file-client-secret"


def test_avito_settings_from_env_requires_client_id(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    clear_avito_env(monkeypatch)
    env_file = write_env_file(
        tmp_path / ".env",
        "AVITO_AUTH__CLIENT_SECRET=client-secret\n",
    )

    with pytest.raises(ConfigurationError, match="client_id"):
        AvitoSettings.from_env(env_file=env_file)


def test_avito_settings_from_env_requires_client_secret(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    clear_avito_env(monkeypatch)
    env_file = write_env_file(
        tmp_path / ".env",
        "AVITO_AUTH__CLIENT_ID=client-id\n",
    )

    with pytest.raises(ConfigurationError, match="client_secret"):
        AvitoSettings.from_env(env_file=env_file)


def test_avito_client_from_env_initializes_client(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    clear_avito_env(monkeypatch)
    env_file = write_env_file(
        tmp_path / ".env",
        "\n".join(
            (
                "AVITO_BASE_URL=https://sandbox.avito.ru",
                "AVITO_USER_ID=512",
                "AVITO_AUTH__CLIENT_ID=client-id",
                "AVITO_AUTH__CLIENT_SECRET=client-secret",
            )
        ),
    )

    client = AvitoClient.from_env(env_file=env_file)
    try:
        assert client.settings.base_url == "https://sandbox.avito.ru"
        assert client.settings.user_id == 512
        assert client.settings.auth.client_id == "client-id"
        assert client.settings.auth.client_secret == "client-secret"
    finally:
        client.close()


def test_avito_client_requires_explicit_auth_fields() -> None:
    with pytest.raises(ConfigurationError, match="client_secret"):
        AvitoClient(AvitoSettings(auth=AuthSettings(client_id="client-id")))


def test_explicit_settings_do_not_implicitly_read_process_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AVITO_CLIENT_SECRET", "from-process-env")

    settings = AvitoSettings(auth=AuthSettings(client_id="client-id"))

    assert settings.auth.client_secret is None


def test_debug_info_does_not_expose_secret_values(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    clear_avito_env(monkeypatch)
    client = AvitoClient.from_env(
        env_file=write_env_file(
            tmp_path / ".env",
            "\n".join(
                (
                    "AVITO_BASE_URL=https://sandbox.avito.ru",
                    "AVITO_USER_ID=99",
                    "AVITO_AUTH__CLIENT_ID=client-id",
                    "AVITO_AUTH__CLIENT_SECRET=super-secret",
                )
            ),
        )
    )
    try:
        info = client.debug_info()

        assert info.base_url == "https://sandbox.avito.ru"
        assert info.user_id == 99
        assert "super-secret" not in repr(info)
        assert "authorization" not in repr(info).lower()
    finally:
        client.close()


def test_process_environment_overrides_dotenv_deterministically(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    clear_avito_env(monkeypatch)
    env_file = write_env_file(
        tmp_path / ".env",
        "\n".join(
            (
                "AVITO_BASE_URL=https://from-file.avito.ru",
                "AVITO_AUTH__CLIENT_ID=file-client-id",
                "AVITO_AUTH__CLIENT_SECRET=file-client-secret",
            )
        ),
    )
    monkeypatch.setenv("AVITO_BASE_URL", "https://from-env.avito.ru")
    monkeypatch.setenv("AVITO_CLIENT_ID", "env-client-id")
    monkeypatch.setenv("AVITO_SECRET", "env-client-secret")

    settings = AvitoSettings.from_env(env_file=env_file)

    assert settings.base_url == "https://from-env.avito.ru"
    assert settings.auth.client_id == "env-client-id"
    assert settings.auth.client_secret == "env-client-secret"
