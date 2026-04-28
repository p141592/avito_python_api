# Swagger Binding Decorator

## Цель

В SDK должен быть единый машинно-проверяемый способ связать публичный SDK-метод с операцией из Swagger-спецификации.

Swagger-файлы в `docs/avito/api/*.json` являются единственным источником истины по API-контракту:

- HTTP method;
- path;
- path/query/header parameters;
- request body;
- content-type;
- response statuses;
- response schemas;
- error schemas;
- deprecated state.

Декоратор и class-level metadata не должны дублировать API-контракт. Они описывают только:

```text
какой SDK method соответствует какой Swagger operation
как contract-test runner должен вызвать этот SDK method
```

## 1. Публичный API Декоратора

Модуль:

```text
avito/core/swagger.py
```

Основной декоратор:

```python
@swagger_operation(
    method: str,
    path: str,
    *,
    spec: str | None = None,
    operation_id: str | None = None,
    factory: str | None = None,
    factory_args: Mapping[str, str] | None = None,
    method_args: Mapping[str, str] | None = None,
    deprecated: bool = False,
    legacy: bool = False,
)
```

Пример:

```python
class Chat:
    __swagger_domain__ = "messenger"
    __swagger_spec__ = "Мессенджер.json"
    __sdk_factory__ = "chat"

    @swagger_operation(
        "GET",
        "/messenger/v1/accounts/{user_id}/chats/{chat_id}",
        factory_args={
            "user_id": "path.user_id",
            "chat_id": "path.chat_id",
        },
    )
    def get(self) -> ChatInfo:
        ...
```

## 2. Class-Level Metadata

Публичные domain objects и section clients могут объявлять служебные поля:

```python
__swagger_domain__: str
__swagger_spec__: str
__sdk_factory__: str
__sdk_factory_args__: Mapping[str, str]
```

Назначение:

```text
__swagger_domain__
    Логический домен SDK: ads, messenger, orders, promotion, accounts и т.д.
    Используется для группировки contract tests и отчетов линтера.

__swagger_spec__
    Имя Swagger-файла из docs/avito/api/.
    Используется как default spec для всех decorated методов класса.

__sdk_factory__
    Имя factory method на AvitoClient.
    Например: "chat" означает client.chat(...).

__sdk_factory_args__
    Default mapping аргументов factory.
    Используется, если method-level factory_args не указан.
```

Приоритет значений:

```text
1. Значения из @swagger_operation(...)
2. Значения из class-level metadata
3. Auto-resolve через Swagger registry, если это безопасно и однозначно
```

## 3. Binding Model

Декоратор должен записывать metadata в атрибут функции:

```python
func.__swagger_binding__
```

Тип:

```python
@dataclass(frozen=True, slots=True)
class SwaggerOperationBinding:
    method: str
    path: str
    spec: str | None
    operation_id: str | None
    factory: str | None
    factory_args: Mapping[str, str]
    method_args: Mapping[str, str]
    deprecated: bool
    legacy: bool
```

Требования:

- `method` нормализуется в uppercase.
- `path` хранится в Swagger-формате: `/path/{param}`.
- `factory_args` и `method_args` внутри модели должны быть immutable mapping.
- Декоратор не должен менять поведение метода.
- Декоратор не должен выполнять загрузку Swagger-файлов на import time.

## 4. Запрещенные Поля

В декораторе запрещены любые поля, дублирующие Swagger-контракт:

```python
response_model=...
request_model=...
request_schema=...
response_schema=...
success_statuses=...
error_statuses=...
content_type=...
required_fields=...
query_params=...
path_params=...
```

Причина: это создает второй источник истины и допускает расхождение со Swagger.

## 5. Path Expressions

`factory_args` и `method_args` описывают, как contract-test runner строит SDK-вызов из Swagger-generated request data.

Разрешенные выражения:

```text
path.<name>       path parameter
query.<name>      query parameter
header.<name>     header parameter
body              весь request body
body.<field>      поле request body
constant.<name>   тестовая константа из controlled test registry
```

Примеры:

```python
factory_args={
    "user_id": "path.user_id",
    "item_id": "path.item_id",
}
```

```python
method_args={
    "request": "body",
}
```

```python
method_args={
    "limit": "query.limit",
    "offset": "query.offset",
}
```

Ограничения:

- `factory_args` и `method_args` не должны содержать Python expressions.
- Запрещены произвольные callables.
- Запрещены dotted paths, которые не относятся к Swagger request.
- `constant.*` разрешается только для заранее зарегистрированных тестовых констант.

## 6. Swagger Operation Identity

Операция определяется ключом:

```text
spec + method + normalized_path
```

Если `spec` не указан, operation может быть найдена по:

```text
method + normalized_path
```

только если совпадение среди всех Swagger-файлов ровно одно.

`operation_id`, если указан, является дополнительной проверкой, а не основным источником истины.

## 7. Линтер

Нужен отдельный CLI-линтер:

```bash
poetry run python scripts/lint_swagger_bindings.py
```

И make target:

```bash
make swagger-lint
```

Линтер должен запускаться вместе с общей проверкой качества проекта.

## 8. Что Проверяет Линтер

### 8.1 Swagger Files

Линтер загружает все файлы:

```text
docs/avito/api/*.json
```

Проверяет:

- JSON валиден;
- Swagger/OpenAPI структура поддерживается;
- все paths и operations извлекаются;
- каждая operation имеет стабильный ключ;
- нет дублей `spec + method + path`;
- path parameters в path совпадают с parameters/request definition.

### 8.2 SDK Binding Discovery

Линтер импортирует пакет `avito` и находит все функции/методы с:

```python
__swagger_binding__
```

Для каждого binding определяет:

- module;
- class name;
- method name;
- effective `spec`;
- effective `factory`;
- effective `factory_args`;
- effective `method_args`;
- class-level metadata.

### 8.3 Completeness

Обязательные проверки:

```text
1. Каждая Swagger operation имеет ровно один SDK binding.
2. Каждый SDK binding указывает на существующую Swagger operation.
3. Две SDK methods не могут ссылаться на одну Swagger operation.
4. Один SDK method не может иметь несколько bindings, кроме явно разрешенной политики.
5. spec из binding/class metadata должен существовать в docs/avito/api/.
6. method/path должны совпадать с operation из Swagger.
7. operation_id, если указан, должен совпадать со Swagger.
```

### 8.4 Deprecated / Legacy

Проверки:

```text
1. Если Swagger operation deprecated=true, binding должен иметь deprecated=True.
2. Если binding deprecated=True, Swagger operation тоже должна быть deprecated.
3. Если политика SDK требует legacy domain для deprecated operations, binding должен иметь legacy=True.
4. Non-deprecated operation не может иметь legacy=True без явного исключения.
```

Исключения, если они понадобятся, должны быть описаны в отдельном allowlist-файле с причиной и датой удаления. По умолчанию allowlist запрещен.

### 8.5 Factory Validation

Для каждого binding:

```text
1. factory должен существовать на AvitoClient.
2. Если factory не указан в decorator, должен быть __sdk_factory__ на классе.
3. factory_args должны соответствовать сигнатуре factory.
4. method_args должны соответствовать сигнатуре decorated SDK method.
5. Required параметры factory/method должны быть покрыты mapping-ом.
6. В mapping не должно быть лишних аргументов.
```

### 8.6 Path Expression Validation

Для каждого выражения в `factory_args` и `method_args`:

```text
path.<name>
    <name> должен существовать среди path parameters Swagger operation.

query.<name>
    <name> должен существовать среди query parameters Swagger operation.

header.<name>
    <name> должен существовать среди header parameters Swagger operation.

body
    Swagger operation должна иметь request body.

body.<field>
    Swagger operation должна иметь request body schema, где поле существует.

constant.<name>
    <name> должен существовать в test constants registry.
```

### 8.7 Запрет Дублирования Контракта

Линтер должен падать, если в `SwaggerOperationBinding` или decorator call появляются запрещенные поля:

- statuses;
- schemas;
- content types;
- response models;
- request models;
- error models.

Это можно проверять через сигнатуру декоратора и unit-тесты самого декоратора.

## 9. Формат Ошибок Линтера

Ошибка должна быть точной и actionable.

Пример:

```text
[SWAGGER_BINDING_NOT_FOUND]
Swagger operation has no SDK binding:
spec=Мессенджер.json
method=GET
path=/messenger/v1/accounts/{user_id}/chats/{chat_id}
```

```text
[SWAGGER_BINDING_DUPLICATE]
Multiple SDK methods bind the same Swagger operation:
spec=Объявления.json
method=GET
path=/core/v1/items/{item_id}
methods:
- avito.ads.domain.Ad.get
- avito.ads.client.AdsClient.get_item
```

```text
[SWAGGER_ARG_UNKNOWN_QUERY_PARAM]
Binding references unknown query parameter:
method=avito.messenger.domain.Chat.list
expression=query.page
swagger_operation=GET /messenger/v1/accounts/{user_id}/chats
known_query_params=[limit, offset]
```

## 10. Не Цель Декоратора

Декоратор не должен:

- генерировать SDK-код;
- валидировать реальные payload на runtime;
- выполнять HTTP;
- знать response statuses;
- знать schemas;
- заменять Swagger;
- заменять typed models.

Runtime/request/response проверки делает `SwaggerFakeTransport` и contract tests, используя Swagger operation, найденную через binding.

## Итоговый Инвариант

```text
Swagger operation
↔ exactly one @swagger_operation SDK method
→ SwaggerFakeTransport validates actual HTTP request/response
→ contract tests validate all statuses and errors from Swagger
```

Декоратор дает строгую адресацию. Линтер гарантирует, что адресация полная и валидная. Swagger остается единственным источником API-контракта.
