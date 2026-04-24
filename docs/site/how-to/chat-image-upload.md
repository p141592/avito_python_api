# Чаты, сообщения и изображения

Этот рецепт показывает базовый цикл работы с мессенджером: найти чат, прочитать сообщения, отправить текст, загрузить изображение и отправить его в чат.

## Список чатов

Для операций мессенджера почти всегда нужен `user_id`. Передайте его в фабрику доменного объекта.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    chats = avito.chat(user_id=7).list()

print(chats.items[0].chat_id)
print(chats.items[0].last_message_text)
```

## Карточка и сообщения чата

`chat()` отвечает за состояние чата, а `chat_message()` — за сообщения внутри него.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    chat = avito.chat("chat-1", user_id=7).get()
    messages = avito.chat_message(chat_id="chat-1", user_id=7).list()

print(chat.title)
print(messages.items[0].text)
```

## Отправка текста

Для повторяемых write-вызовов передавайте `idempotency_key`.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    sent = avito.chat_message(chat_id="chat-1", user_id=7).send_message(
        message="Здравствуйте, объявление актуально.",
        idempotency_key="chat-text-example-1",
    )

print(sent.message_id)
print(sent.status)
```

## Загрузка изображения

`upload_images()` принимает список `UploadImageFile`. В пользовательском коде `content` может быть bytes или file-like объектом.

```python
from avito import AvitoClient
from avito.messenger import UploadImageFile

image = UploadImageFile(
    field_name="image",
    filename="photo.jpg",
    content=b"image-bytes",
    content_type="image/jpeg",
)

with AvitoClient.from_env() as avito:
    uploaded = avito.chat_media(user_id=7).upload_images(
        files=[image],
        idempotency_key="chat-upload-example-1",
    )

print(uploaded.items[0].image_id)
```

## Отправка изображения

После загрузки используйте `image_id` в `send_image()`.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    result = avito.chat_message(chat_id="chat-1", user_id=7).send_image(
        image_id="img-1",
        caption="Фото товара",
        idempotency_key="chat-image-example-1",
    )

print(result.message_id)
```

## Пометка чата прочитанным

Состояние чата меняется через `chat().mark_read()`.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    result = avito.chat("chat-1", user_id=7).mark_read(
        idempotency_key="chat-read-example-1",
    )

print(result.success)
```

Полный контракт моделей смотрите в [reference по messenger](../reference/domains/messenger.md). Для webhook и спецпредложений используйте отдельные доменные объекты `chat_webhook()` и `special_offer_campaign()`.
