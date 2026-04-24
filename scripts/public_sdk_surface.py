from __future__ import annotations

import importlib
import inspect
from collections.abc import Callable
from dataclasses import dataclass

try:
    from parse_inventory import InventoryRow
except ModuleNotFoundError:
    from scripts.parse_inventory import InventoryRow


@dataclass(slots=True, frozen=True)
class PublicMethod:
    sdk_package: str
    domain_object: str
    method_name: str
    method: object

    @property
    def symbol(self) -> str:
        return f"avito.{self.sdk_package}.{self.domain_object}.{self.method_name}"


MethodAlias = Callable[[InventoryRow], str | None]


EXPLICIT_METHOD_ALIASES: dict[tuple[str, str, str], str] = {
    ("accounts", "Account", "get_user_info_self"): "get_self",
    ("accounts", "Account", "get_user_balance"): "get_balance",
    ("accounts", "AccountHierarchy", "get_check_ah_user_v1"): "get_status",
    ("accounts", "AccountHierarchy", "list_employees_v1"): "list_employees",
    ("accounts", "AccountHierarchy", "create_link_items_v1"): "link_items",
    ("accounts", "AccountHierarchy", "list_company_phones_v1"): "list_company_phones",
    ("accounts", "AccountHierarchy", "list_items_by_employee_id_v1"): "list_items_by_employee",
    ("ads", "Ad", "get_item_info"): "get",
    ("ads", "Ad", "get_items_info"): "list",
    ("ads", "Ad", "update_update_price"): "update_price",
    ("ads", "AdPromotion", "update_item_vas"): "apply_vas_direct",
    ("ads", "AdPromotion", "update_item_vas_package_v2"): "apply_vas_package",
    ("ads", "AdPromotion", "update_apply_vas"): "apply_vas",
    ("ads", "AdStats", "get_item_stats_shallow"): "get_item_stats",
    ("ads", "AutoloadProfile", "create_upload"): "upload_by_url",
    ("ads", "AutoloadProfile", "get_user_docs_node_fields"): "get_node_fields",
    ("ads", "AutoloadProfile", "get_user_docs_tree"): "get_tree",
    ("ads", "AutoloadProfile", "get_profile_v2"): "get",
    ("ads", "AutoloadProfile", "create_or_update_profile_v2"): "save",
    ("ads", "AutoloadReport", "list_reports_v2"): "list",
    ("ads", "AutoloadReport", "get_autoload_items_info_v2"): "get_items_info",
    ("ads", "AutoloadReport", "get_report_items_by_id"): "get_items",
    ("ads", "AutoloadReport", "get_report_items_fees_by_id"): "get_fees",
    ("ads", "AutoloadReport", "get_last_completed_report_v3"): "get_last_completed",
    ("ads", "AutoloadReport", "get_report_by_id_v3"): "get",
    ("autoteka", "AutotekaVehicle", "get_catalogs_resolve"): "resolve_catalog",
    ("autoteka", "AutotekaMonitoring", "list_monitoring_bucket_delete"): "remove_bucket",
    ("autoteka", "AutotekaMonitoring", "delete_monitoring_bucket_remove"): "delete_bucket",
    (
        "autoteka",
        "AutotekaMonitoring",
        "get_monitoring_get_reg_actions",
    ): "get_monitoring_reg_actions",
    ("autoteka", "AutotekaReport", "list_report_list"): "list_reports",
    ("autoteka", "AutotekaScoring", "get_scoring_get_by_id"): "get_scoring_by_id",
    ("autoteka", "AutotekaVehicle", "get_specification_get_by_id"): "get_specification_by_id",
    (
        "autoteka",
        "AutotekaReport",
        "create_sync_create_report_by_reg_number",
    ): "create_sync_report_by_reg_number",
    (
        "autoteka",
        "AutotekaReport",
        "create_sync_create_report_by_vin",
    ): "create_sync_report_by_vin",
    ("cpa", "CpaChat", "get_chat_by_action_id"): "get",
    ("cpa", "CpaCall", "create_create_complaint"): "create_complaint",
    ("cpa", "CpaCall", "create_calls_by_time_v2"): "list",
    ("cpa", "CpaChat", "create_chats_by_time"): "list",
    ("cpa", "CpaLead", "create_balance_info_v3"): "get_balance_info",
    ("cpa", "CallTrackingCall", "create_call_by_id"): "get",
    ("cpa", "CallTrackingCall", "create_calls"): "list",
    ("cpa", "CallTrackingCall", "get_record_by_call_id"): "download",
    ("jobs", "Application", "get_applications_apply_actions"): "apply",
    ("jobs", "Application", "list_applications_get_by_ids"): "list",
    ("jobs", "Application", "list_applications_get_ids"): "list",
    ("jobs", "Application", "list_applications_get_states"): "get_states",
    ("jobs", "Application", "get_applications_set_is_viewed"): "update",
    ("jobs", "JobWebhook", "delete_applications_webhook_delete"): "delete",
    ("jobs", "JobWebhook", "get_applications_webhook_get"): "get",
    ("jobs", "JobWebhook", "update_applications_webhook_put"): "update",
    ("jobs", "JobWebhook", "list_applications_webhooks_get"): "list",
    ("jobs", "Resume", "list_resumes_get"): "list",
    ("jobs", "Resume", "get_resume_get_contacts"): "get_contacts",
    ("jobs", "Resume", "get_resume_get_item"): "get",
    ("jobs", "Vacancy", "create_vacancy_create"): "create",
    ("jobs", "Vacancy", "delete_vacancy_archive"): "delete",
    ("jobs", "Vacancy", "update_vacancy_update"): "update",
    ("jobs", "Vacancy", "create_vacancy_prolongate"): "prolongate",
    ("jobs", "Vacancy", "list_search_vacancy"): "list",
    ("jobs", "Vacancy", "create_vacancy_create_v2"): "create",
    ("jobs", "Vacancy", "get_vacancies_get_by_ids"): "get_by_ids",
    ("jobs", "Vacancy", "get_vacancy_get_statuses"): "get_statuses",
    ("jobs", "Vacancy", "update_vacancy_update_v2"): "update",
    ("jobs", "Vacancy", "get_vacancy_get_item"): "get",
    ("jobs", "Vacancy", "update_vacancy_auto_renewal"): "update_auto_renewal",
    ("jobs", "JobDictionary", "list_dicts"): "list",
    ("jobs", "JobDictionary", "list_dict_by_id"): "get",
    ("messenger", "ChatMessage", "create_send_message"): "send_message",
    ("messenger", "ChatMessage", "create_send_image_message"): "send_image",
    ("messenger", "ChatMessage", "delete_message"): "delete",
    ("messenger", "Chat", "create_chat_read"): "mark_read",
    ("messenger", "ChatMedia", "create_upload_images"): "upload_images",
    ("messenger", "ChatWebhook", "get_subscriptions"): "list",
    ("messenger", "ChatWebhook", "delete_webhook_unsubscribe"): "unsubscribe",
    ("messenger", "Chat", "create_blacklist_v2"): "blacklist",
    ("messenger", "Chat", "get_chats_v2"): "list",
    ("messenger", "Chat", "get_chat_by_id_v2"): "get",
    ("messenger", "ChatMessage", "list_messages_v3"): "list",
    ("messenger", "ChatWebhook", "update_webhook_v3"): "subscribe",
    ("messenger", "SpecialOfferCampaign", "create_multi_confirm"): "confirm_multi",
    ("messenger", "SpecialOfferCampaign", "create_multi_create"): "create_multi",
    ("orders", "DeliveryOrder", "delete_cancel_announcement3_pl"): "delete",
    ("orders", "DeliveryOrder", "create_announcement3_pl"): "create_announcement",
    ("orders", "DeliveryOrder", "create_parcel"): "create",
    ("orders", "DeliveryTask", "get_task"): "get",
    ("orders", "Order", "create_accept_return_order"): "accept_return_order",
    ("orders", "Order", "get_apply_transition"): "apply",
    ("orders", "Order", "create_check_confirmation_code"): "check_confirmation_code",
    ("orders", "Order", "create_cnc_set_details"): "set_cnc_details",
    ("orders", "Order", "get_set_courier_delivery_range"): "set_courier_delivery_range",
    ("orders", "Order", "update_set_order_tracking_number"): "update_tracking_number",
    ("orders", "Order", "get_orders"): "list",
    ("orders", "OrderLabel", "create_generate_labels"): "create",
    ("orders", "OrderLabel", "create_generate_labels_extended"): "create",
    ("orders", "OrderLabel", "get_download_label"): "download",
    ("orders", "Stock", "get_получение_остатков"): "get",
    ("orders", "Stock", "update_редактирование_остатков"): "update",
    ("promotion", "TrxPromotion", "create_trx_promo_open_api_apply"): "apply",
    ("promotion", "TrxPromotion", "delete_trx_promo_open_api_cancel"): "delete",
    ("promotion", "TrxPromotion", "get_trx_promo_open_api_commissions"): "get_commissions",
    ("promotion", "AutostrategyCampaign", "create_autostrategy_budget"): "create_budget",
    ("promotion", "AutostrategyCampaign", "create_autostrategy_campaign"): "create",
    (
        "promotion",
        "AutostrategyCampaign",
        "update_edit_autostrategy_campaign",
    ): "update",
    (
        "promotion",
        "AutostrategyCampaign",
        "get_autostrategy_campaign_info",
    ): "get",
    (
        "promotion",
        "AutostrategyCampaign",
        "delete_stop_autostrategy_campaign",
    ): "delete",
    ("promotion", "AutostrategyCampaign", "list_autostrategy_campaigns"): "list",
    ("promotion", "AutostrategyCampaign", "get_autostrategy_stat"): "get_stat",
    ("promotion", "TargetActionPricing", "delete_promotion"): "delete",
    ("promotion", "TargetActionPricing", "update_auto_bid"): "update_auto",
    ("promotion", "TargetActionPricing", "update_manual_bid"): "update_manual",
    ("promotion", "BbipPromotion", "create_bbip_forecasts_by_items_v1"): "get_forecasts",
    ("promotion", "BbipPromotion", "update_bbip_order_for_items_v1"): "create_order",
    ("promotion", "BbipPromotion", "create_bbip_suggests_by_items_v1"): "get_suggests",
    ("promotion", "PromotionOrder", "create_dict_of_services_v1"): "get_service_dictionary",
    ("promotion", "PromotionOrder", "list_services_by_items_v1"): "list_services",
    ("promotion", "PromotionOrder", "list_orders_by_user_v1"): "list_orders",
    ("promotion", "PromotionOrder", "get_order_status_v1"): "get_order_status",
    (
        "realty",
        "RealtyAnalyticsReport",
        "get_market_price_correspondence_v1",
    ): "get_market_price_correspondence",
    ("ratings", "ReviewAnswer", "create_review_answer_v1"): "create",
    ("ratings", "ReviewAnswer", "delete_review_answer_v1"): "delete",
    ("ratings", "RatingProfile", "get_ratings_info_v1"): "get",
    ("ratings", "Review", "list_reviews_v1"): "list",
}

SANDBOX_DELIVERY_ALIASES: dict[str, str] = {
    "create_track_announcement": "track_announcement",
    "delete_cancel_parcel": "cancel_parcel",
    "get_check_confirmation_code": "check_confirmation_code",
    "create_set_order_properties": "set_order_properties",
    "create_set_order_real_address": "set_order_real_address",
    "create_tracking": "tracking",
    "delete_prohibit_order_acceptance": "prohibit_order_acceptance",
    "create_add_sorting_center": "add_sorting_center",
    "create_add_areas_sandbox": "add_areas",
    "update_add_tags_to_sorting_center": "add_tags_to_sorting_center",
    "create_add_terminals_sandbox": "add_terminals",
    "update_update_terms": "update_terms",
    "create_add_tariff_sandbox_v2": "add_tariff",
    "create_v1cancel_announcement": "cancel_sandbox_announcement",
    "delete_v1_cancel_parcel": "cancel_sandbox_parcel",
    "create_v1change_parcel": "change_sandbox_parcel",
    "create_v1create_announcement": "create_sandbox_announcement",
    "get_v1get_announcement_event": "get_sandbox_announcement_event",
    "get_v1get_change_parcel_info": "get_sandbox_change_parcel_info",
    "get_v1get_parcel_info": "get_sandbox_parcel_info",
    "get_v1get_registered_parcel_id": "get_sandbox_registered_parcel_id",
    "create_sandbox_parcel_v2": "create_parcel",
}


def resolve_public_method(row: InventoryRow) -> PublicMethod | None:
    if row.domain_object == "AvitoClient.auth()":
        from avito import AvitoClient

        method = getattr(AvitoClient, "auth", None)
        if method is None:
            return None
        return PublicMethod("client", "AvitoClient", "auth", method)

    try:
        module = importlib.import_module(f"avito.{row.sdk_package}")
    except ModuleNotFoundError:
        return None

    domain_class = getattr(module, row.domain_object, None)
    if domain_class is None or not inspect.isclass(domain_class):
        return None

    method_name = public_method_name(row)
    method = getattr(domain_class, method_name, None)
    if method is None:
        return None
    return PublicMethod(row.sdk_package, row.domain_object, method_name, method)


def public_method_name(row: InventoryRow) -> str:
    explicit = EXPLICIT_METHOD_ALIASES.get(
        (row.sdk_package, row.domain_object, row.sdk_public_method)
    )
    if explicit is not None:
        return explicit
    if row.sdk_package == "orders" and row.domain_object == "SandboxDelivery":
        return SANDBOX_DELIVERY_ALIASES.get(row.sdk_public_method, row.sdk_public_method)
    return row.sdk_public_method
