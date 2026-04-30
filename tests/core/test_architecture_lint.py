from __future__ import annotations

from pathlib import Path

from lint_architecture import (
    DEFAULT_MIGRATION_ALLOWLIST,
    lint_architecture,
    render_text_report,
)


def test_lint_architecture_current_migration_baseline_has_no_errors() -> None:
    errors = lint_architecture(Path("."), allowlisted_domains=DEFAULT_MIGRATION_ALLOWLIST)

    assert errors == ()


def test_lint_architecture_rejects_legacy_files_outside_allowlist(tmp_path: Path) -> None:
    _write(tmp_path / "avito/tariffs/client.py", "")

    errors = lint_architecture(tmp_path, allowlisted_domains=())

    assert [error.code for error in errors] == ["ARCH_LEGACY_FILE"]
    assert errors[0].path == "avito/tariffs/client.py"


def test_lint_architecture_allows_legacy_files_for_migration_domain(tmp_path: Path) -> None:
    _write(tmp_path / "avito/tariffs/client.py", "")

    errors = lint_architecture(tmp_path, allowlisted_domains=("tariffs",))

    assert errors == ()


def test_lint_architecture_rejects_underscore_prefixed_legacy_files(tmp_path: Path) -> None:
    _write(tmp_path / "avito/tariffs/_client.py", "")
    _write(tmp_path / "avito/tariffs/_mapping.py", "")
    _write(tmp_path / "avito/tariffs/_enums.py", "")

    errors = lint_architecture(tmp_path, allowlisted_domains=())

    paths = sorted(error.path for error in errors if error.code == "ARCH_LEGACY_FILE")
    assert paths == [
        "avito/tariffs/_client.py",
        "avito/tariffs/_enums.py",
        "avito/tariffs/_mapping.py",
    ]


def test_lint_architecture_rejects_underscore_prefixed_legacy_imports(tmp_path: Path) -> None:
    _write(
        tmp_path / "avito/summary/models.py",
        "from avito.tariffs._enums import TariffLevel\n",
    )

    errors = lint_architecture(tmp_path, allowlisted_domains=())

    codes = [error.code for error in errors]
    assert "ARCH_LEGACY_IMPORT" in codes


def test_lint_architecture_rejects_legacy_import_and_usage(tmp_path: Path) -> None:
    legacy_call = "request_" + "public_model"
    legacy_mapper = "mapper" + "="
    _write(
        tmp_path / "avito/summary/models.py",
        "\n".join(
            [
                "from avito.tariffs." + "enums import TariffLevel",
                "",
                "def call(transport):",
                f"    return transport.{legacy_call}({legacy_mapper}None)",
            ]
        ),
    )

    errors = lint_architecture(tmp_path, allowlisted_domains=())

    assert [error.code for error in errors] == [
        "ARCH_LEGACY_IMPORT",
        "ARCH_LEGACY_USAGE",
        "ARCH_LEGACY_USAGE",
    ]


def test_lint_architecture_rejects_public_method_without_v2_contract(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "avito/tariffs/domain.py",
        "\n".join(
            [
                "class Tariff:",
                "    def get_tariff_info(self) -> dict[str, object]:",
                "        return {}",
            ]
        ),
    )

    errors = lint_architecture(tmp_path, allowlisted_domains=())

    assert [error.code for error in errors] == [
        "ARCH_PUBLIC_METHOD_NO_OPERATION_SPEC",
        "ARCH_PUBLIC_METHOD_UNBOUND",
        "ARCH_PUBLIC_RETURN_RAW",
    ]


def test_lint_architecture_accepts_public_method_with_swagger_and_execute(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "avito/tariffs/domain.py",
        "\n".join(
            [
                "class Tariff:",
                "    @swagger_operation('GET', '/tariff/info/1')",
                "    def get_tariff_info(self) -> TariffInfo:",
                "        return self._execute(GET_TARIFF_INFO)",
            ]
        ),
    )

    errors = lint_architecture(tmp_path, allowlisted_domains=())

    assert errors == ()


def test_lint_architecture_validates_models_referenced_by_operation_spec(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "avito/tariffs/operations.py",
        "\n".join(
            [
                "GET_TARIFF_INFO = OperationSpec(",
                "    name='tariffs.info.get',",
                "    method='GET',",
                "    path='/tariff/info/1',",
                "    query_model=TariffQuery,",
                "    request_model=TariffRequest,",
                "    response_model=TariffInfo,",
                ")",
            ]
        ),
    )
    _write(
        tmp_path / "avito/tariffs/models.py",
        "\n".join(
            [
                "class TariffQuery:",
                "    pass",
                "",
                "class TariffRequest:",
                "    pass",
                "",
                "class TariffInfo:",
                "    pass",
            ]
        ),
    )

    errors = lint_architecture(tmp_path, allowlisted_domains=())

    assert [error.code for error in errors] == [
        "ARCH_REQUEST_MODEL_NO_SERIALIZER",
        "ARCH_REQUEST_MODEL_NO_SERIALIZER",
        "ARCH_RESPONSE_MODEL_NO_FROM_PAYLOAD",
    ]


def test_lint_architecture_accepts_operation_spec_models_with_v2_contracts(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "avito/tariffs/operations.py",
        "\n".join(
            [
                "GET_TARIFF_INFO = OperationSpec(",
                "    name='tariffs.info.get',",
                "    method='GET',",
                "    path='/tariff/info/1',",
                "    query_model=TariffQuery,",
                "    request_model=TariffRequest,",
                "    response_model=TariffInfo,",
                ")",
            ]
        ),
    )
    _write(
        tmp_path / "avito/tariffs/models.py",
        "\n".join(
            [
                "class TariffQuery(RequestModel):",
                "    pass",
                "",
                "class TariffRequest:",
                "    def to_payload(self):",
                "        return {}",
                "",
                "class TariffInfo:",
                "    @classmethod",
                "    def from_payload(cls, payload):",
                "        return cls()",
            ]
        ),
    )

    errors = lint_architecture(tmp_path, allowlisted_domains=())

    assert errors == ()


def test_lint_architecture_rejects_runtime_patching_in_production(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "avito/core/dynamic.py", "setattr(object, 'name', value)")

    errors = lint_architecture(tmp_path, allowlisted_domains=())

    assert [error.code for error in errors] == ["ARCH_RUNTIME_PATCHING"]


def test_render_text_report_includes_error_locations() -> None:
    errors = lint_architecture(Path("."), allowlisted_domains=())

    output = render_text_report(errors, allowlisted_domains=())

    assert "Architecture lint:" in output
    assert "allowlisted_domains=-" in output
    assert "avito/orders/_client.py:95: [ARCH_LEGACY_USAGE]" in output


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content + "\n", encoding="utf-8")
