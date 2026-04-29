"""Working factory/domain mapping for Swagger binding rollout."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import cast, get_type_hints

from avito.client import AvitoClient
from avito.core.domain import DomainObject

_PACKAGE_SPEC_CANDIDATES: dict[str, tuple[str, ...]] = {
    "accounts": ("Информацияопользователе.json", "ИерархияАккаунтов.json"),
    "ads": ("Объявления.json", "Автозагрузка.json"),
    "autoteka": ("Автотека.json",),
    "cpa": ("CPAАвито.json", "CallTracking[КТ].json"),
    "jobs": ("АвитоРабота.json",),
    "messenger": ("Мессенджер.json", "Рассылкаскидокиспецпредложенийвмессенджере.json"),
    "orders": ("Доставка.json", "Управлениезаказами.json", "Управлениеостатками.json"),
    "promotion": (
        "Продвижение.json",
        "TrxPromo.json",
        "CPA-аукцион.json",
        "Настройкаценыцелевогодействия.json",
        "Автостратегия.json",
    ),
    "ratings": ("Рейтингииотзывы.json",),
    "realty": ("Краткосрочнаяаренда.json", "Аналитикапонедвижимости.json"),
    "tariffs": ("Тарифы.json",),
}
_CLASS_SPEC_CANDIDATES: dict[str, tuple[str, ...]] = {
    "Account": ("Информацияопользователе.json",),
    "AccountHierarchy": ("ИерархияАккаунтов.json",),
    "Ad": ("Объявления.json",),
    "AdPromotion": ("Объявления.json",),
    "AdStats": ("Объявления.json",),
    "Application": ("АвитоРабота.json",),
    "AutoloadArchive": ("Автозагрузка.json",),
    "AutoloadProfile": ("Автозагрузка.json",),
    "AutoloadReport": ("Автозагрузка.json",),
    "AutostrategyCampaign": ("Автостратегия.json",),
    "AutotekaMonitoring": ("Автотека.json",),
    "AutotekaReport": ("Автотека.json",),
    "AutotekaScoring": ("Автотека.json",),
    "AutotekaValuation": ("Автотека.json",),
    "AutotekaVehicle": ("Автотека.json",),
    "BbipPromotion": ("Продвижение.json",),
    "CallTrackingCall": ("CallTracking[КТ].json",),
    "Chat": ("Мессенджер.json",),
    "ChatMedia": ("Мессенджер.json",),
    "ChatMessage": ("Мессенджер.json",),
    "ChatWebhook": ("Мессенджер.json",),
    "CpaArchive": ("CPAАвито.json",),
    "CpaAuction": ("CPA-аукцион.json",),
    "CpaCall": ("CPAАвито.json",),
    "CpaChat": ("CPAАвито.json",),
    "CpaLead": ("CPAАвито.json",),
    "DeliveryOrder": ("Доставка.json",),
    "DeliveryTask": ("Доставка.json",),
    "JobDictionary": ("АвитоРабота.json",),
    "JobWebhook": ("АвитоРабота.json",),
    "Order": ("Управлениезаказами.json",),
    "OrderLabel": ("Доставка.json",),
    "PromotionOrder": ("Продвижение.json",),
    "RatingProfile": ("Рейтингииотзывы.json",),
    "RealtyAnalyticsReport": ("Аналитикапонедвижимости.json",),
    "RealtyBooking": ("Краткосрочнаяаренда.json",),
    "RealtyListing": ("Краткосрочнаяаренда.json",),
    "RealtyPricing": ("Краткосрочнаяаренда.json",),
    "Resume": ("АвитоРабота.json",),
    "Review": ("Рейтингииотзывы.json",),
    "ReviewAnswer": ("Рейтингииотзывы.json",),
    "SandboxDelivery": ("Доставка.json",),
    "SpecialOfferCampaign": ("Рассылкаскидокиспецпредложенийвмессенджере.json",),
    "Stock": ("Управлениеостатками.json",),
    "TargetActionPricing": ("Настройкаценыцелевогодействия.json",),
    "Tariff": ("Тарифы.json",),
    "TrxPromotion": ("TrxPromo.json",),
    "Vacancy": ("АвитоРабота.json",),
}


@dataclass(frozen=True, slots=True)
class FactoryDomainMapping:
    """One AvitoClient factory mapped to a public domain class."""

    factory: str
    domain_class: str
    module: str
    package: str
    factory_args: tuple[str, ...]
    spec_candidates: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ClientHelperMethod:
    """Public AvitoClient method that must not receive a direct Swagger binding."""

    method: str
    return_type: str
    reason: str


@dataclass(frozen=True, slots=True)
class FactoryDomainMappingReport:
    """Non-authoritative helper report for domain binding rollout."""

    factories: tuple[FactoryDomainMapping, ...]
    helper_methods: tuple[ClientHelperMethod, ...]

    def to_dict(self) -> dict[str, object]:
        """Return JSON-compatible report data."""

        return {
            "factories": [
                {
                    "factory": mapping.factory,
                    "domain_class": mapping.domain_class,
                    "module": mapping.module,
                    "package": mapping.package,
                    "factory_args": list(mapping.factory_args),
                    "spec_candidates": list(mapping.spec_candidates),
                }
                for mapping in self.factories
            ],
            "helper_methods": [
                {
                    "method": helper.method,
                    "return_type": helper.return_type,
                    "reason": helper.reason,
                }
                for helper in self.helper_methods
            ],
        }


def build_factory_domain_mapping_report() -> FactoryDomainMappingReport:
    """Inspect AvitoClient factories without constructing AvitoClient."""

    factories: list[FactoryDomainMapping] = []
    helper_methods: list[ClientHelperMethod] = []
    for method_name, method in inspect.getmembers(AvitoClient, inspect.isfunction):
        if method_name.startswith("_"):
            continue
        return_type = _return_type(method)
        if _is_domain_class(return_type):
            factories.append(
                _build_factory_mapping(
                    method_name,
                    cast(Callable[..., object], method),
                    cast(type[DomainObject], return_type),
                )
            )
        else:
            helper_methods.append(
                ClientHelperMethod(
                    method=method_name,
                    return_type=_type_name(return_type),
                    reason="summary/helper method; no direct upstream Swagger operation",
                )
            )

    return FactoryDomainMappingReport(
        factories=tuple(sorted(factories, key=lambda item: item.factory)),
        helper_methods=tuple(sorted(helper_methods, key=lambda item: item.method)),
    )


def _return_type(method: object) -> object:
    hints = get_type_hints(method)
    return hints.get("return")


def _is_domain_class(value: object) -> bool:
    return isinstance(value, type) and issubclass(value, DomainObject) and value is not DomainObject


def _build_factory_mapping(
    method_name: str,
    method: Callable[..., object],
    return_type: type[DomainObject],
) -> FactoryDomainMapping:
    package = _package_name(return_type)
    return FactoryDomainMapping(
        factory=method_name,
        domain_class=return_type.__name__,
        module=return_type.__module__,
        package=package,
        factory_args=tuple(_mappable_argument_names(inspect.signature(method))),
        spec_candidates=_CLASS_SPEC_CANDIDATES.get(
            return_type.__name__,
            _PACKAGE_SPEC_CANDIDATES.get(package, ()),
        ),
    )


def _package_name(cls: type[DomainObject]) -> str:
    parts = cls.__module__.split(".")
    return parts[1] if len(parts) > 1 else ""


def _mappable_argument_names(signature: inspect.Signature) -> tuple[str, ...]:
    return tuple(
        name
        for name, parameter in signature.parameters.items()
        if name != "self"
        and parameter.kind
        in {
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        }
    )


def _type_name(value: object) -> str:
    if value is None:
        return "None"
    if isinstance(value, type):
        return f"{value.__module__}.{value.__name__}"
    return str(value)


__all__ = (
    "ClientHelperMethod",
    "FactoryDomainMapping",
    "FactoryDomainMappingReport",
    "build_factory_domain_mapping_report",
)
