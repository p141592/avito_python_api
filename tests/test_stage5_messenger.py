from __future__ import annotations

import json

import httpx

from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts
from avito.messenger import Chat, ChatMedia, ChatMessage, ChatWebhook, SpecialOfferCampaign


def make_transport(handler: httpx.MockTransport) -> Transport:
    settings = AvitoSettings(
        base_url="https://api.avito.ru",
        auth=AuthSettings(),
        retry_policy=RetryPolicy(),
        timeouts=ApiTimeouts(),
    )
    return Transport(
        settings,
        auth_provider=None,
        client=httpx.Client(transport=handler, base_url="https://api.avito.ru"),
        sleep=lambda _: None,
    )


def test_messenger_chat_and_message_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/messenger/v2/accounts/7/chats":
            return httpx.Response(
                200,
                json={
                    "chats": [
                        {"id": "chat-1", "user_id": 7, "title": "Покупатель", "unread_count": 2}
                    ]
                },
            )
        if path == "/messenger/v2/accounts/7/chats/chat-1":
            return httpx.Response(
                200,
                json={
                    "id": "chat-1",
                    "user_id": 7,
                    "title": "Покупатель",
                    "last_message": {"text": "Привет"},
                },
            )
        if path == "/messenger/v1/accounts/7/chats/chat-1/read":
            return httpx.Response(200, json={"success": True, "status": "read"})
        if path == "/messenger/v2/accounts/7/blacklist":
            assert json.loads(request.content.decode()) == {"blacklistedUserId": 99}
            return httpx.Response(200, json={"success": True, "status": "blacklisted"})
        if path == "/messenger/v1/accounts/7/chats/chat-1/messages":
            assert json.loads(request.content.decode()) == {"message": "Здравствуйте"}
            return httpx.Response(
                200, json={"success": True, "message_id": "msg-1", "status": "sent"}
            )
        if path == "/messenger/v3/accounts/7/chats/chat-1/messages/":
            return httpx.Response(
                200,
                json={
                    "messages": [
                        {
                            "id": "msg-1",
                            "chat_id": "chat-1",
                            "text": "Здравствуйте",
                            "direction": "out",
                        }
                    ],
                    "total": 1,
                },
            )
        assert path == "/messenger/v1/accounts/7/chats/chat-1/messages/msg-1"
        return httpx.Response(200, json={"success": True, "status": "deleted"})

    transport = make_transport(httpx.MockTransport(handler))
    chat = Chat(transport, resource_id="chat-1", user_id=7)
    message = ChatMessage(transport, resource_id="msg-1", user_id=7)

    chats = chat.list()
    chat_info = chat.get()
    mark_read = chat.mark_read()
    blacklisted = chat.blacklist(blacklisted_user_id=99)
    sent = message.send_message(chat_id="chat-1", message="Здравствуйте")
    messages = message.list(chat_id="chat-1")
    deleted = message.delete(chat_id="chat-1")

    assert chats.items[0].id == "chat-1"
    assert chat_info.last_message_text == "Привет"
    assert mark_read.status == "read"
    assert blacklisted.status == "blacklisted"
    assert sent.message_id == "msg-1"
    assert messages.total == 1
    assert deleted.status == "deleted"


def test_messenger_media_upload_and_send_image_flow() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/messenger/v1/accounts/7/uploadImages":
            assert request.headers["Content-Type"].startswith("multipart/form-data")
            return httpx.Response(
                200, json={"images": [{"image_id": "img-1", "url": "https://cdn/img-1.jpg"}]}
            )
        if request.url.path == "/messenger/v1/accounts/7/getVoiceFiles":
            return httpx.Response(
                200,
                json={
                    "voice_files": [
                        {"id": "voice-1", "url": "https://cdn/voice.mp3", "duration": 5}
                    ]
                },
            )
        assert request.url.path == "/messenger/v1/accounts/7/chats/chat-1/messages/image"
        assert json.loads(request.content.decode()) == {"imageId": "img-1", "caption": "Фото"}
        return httpx.Response(
            200, json={"success": True, "message_id": "msg-img-1", "status": "sent"}
        )

    transport = make_transport(httpx.MockTransport(handler))
    media = ChatMedia(transport, user_id=7)
    message = ChatMessage(transport, user_id=7)

    uploaded = media.upload_images(files={"image": ("photo.jpg", b"binary", "image/jpeg")})
    voice_files = media.get_voice_files()
    sent = message.send_image(
        chat_id="chat-1", image_id=uploaded.items[0].image_id or "", caption="Фото"
    )

    assert uploaded.items[0].image_id == "img-1"
    assert voice_files.items[0].duration == 5
    assert sent.message_id == "msg-img-1"


def test_messenger_webhook_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/messenger/v1/subscriptions":
            return httpx.Response(
                200,
                json={
                    "subscriptions": [
                        {"url": "https://example.com/hook", "version": "v2", "status": "active"}
                    ]
                },
            )
        if request.url.path == "/messenger/v1/webhook/unsubscribe":
            assert json.loads(request.content.decode()) == {"url": "https://example.com/hook"}
            return httpx.Response(200, json={"success": True, "status": "unsubscribed"})
        assert request.url.path == "/messenger/v3/webhook"
        assert json.loads(request.content.decode()) == {
            "url": "https://example.com/hook",
            "secret": "top-secret",
        }
        return httpx.Response(200, json={"success": True, "status": "subscribed"})

    webhook = ChatWebhook(make_transport(httpx.MockTransport(handler)))

    subscriptions = webhook.list()
    unsubscribed = webhook.unsubscribe(url="https://example.com/hook")
    subscribed = webhook.subscribe(url="https://example.com/hook", secret="top-secret")

    assert subscriptions.items[0].status == "active"
    assert unsubscribed.status == "unsubscribed"
    assert subscribed.status == "subscribed"


def test_special_offer_campaign_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        payload = json.loads(request.content.decode()) if request.content else None
        if path == "/special-offers/v1/available":
            assert payload == {"itemIds": [1, 2]}
            return httpx.Response(
                200, json={"items": [{"item_id": 1, "title": "Объявление", "is_available": True}]}
            )
        if path == "/special-offers/v1/multiCreate":
            assert payload == {"itemIds": [1], "message": "Скидка 10%", "discountPercent": 10}
            return httpx.Response(200, json={"campaign_id": "camp-1", "status": "draft"})
        if path == "/special-offers/v1/multiConfirm":
            assert payload == {"campaignId": "camp-1"}
            return httpx.Response(200, json={"success": True, "status": "confirmed"})
        if path == "/special-offers/v1/stats":
            assert payload == {"campaignId": "camp-1"}
            return httpx.Response(
                200,
                json={
                    "campaign_id": "camp-1",
                    "sent_count": 20,
                    "delivered_count": 18,
                    "read_count": 10,
                },
            )
        assert path == "/special-offers/v1/tariffInfo"
        return httpx.Response(200, json={"price": 9.9, "currency": "RUB", "daily_limit": 100})

    campaign = SpecialOfferCampaign(
        make_transport(httpx.MockTransport(handler)), resource_id="camp-1"
    )

    available = campaign.get_available(item_ids=[1, 2])
    created = campaign.create_multi(item_ids=[1], message="Скидка 10%", discount_percent=10)
    confirmed = campaign.confirm_multi()
    stats = campaign.get_stats()
    tariff = campaign.get_tariff_info()

    assert available.items[0].is_available is True
    assert created.status == "draft"
    assert confirmed.status == "confirmed"
    assert stats.delivered_count == 18
    assert tariff.daily_limit == 100
