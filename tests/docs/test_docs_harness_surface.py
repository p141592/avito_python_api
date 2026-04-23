from __future__ import annotations

import inspect

from avito import AvitoClient
from tests.docs.conftest import build_docs_client


def signature_without_self(callable_object: object) -> inspect.Signature:
    signature = inspect.signature(callable_object)
    parameters = [
        parameter
        for name, parameter in signature.parameters.items()
        if name != "self"
    ]
    return signature.replace(parameters=parameters)


def test_docs_harness_uses_real_public_client_surface() -> None:
    client = build_docs_client()
    account = client.account()

    assert isinstance(client, AvitoClient)
    assert signature_without_self(type(client).account) == inspect.signature(client.account)
    assert signature_without_self(type(account).get_self) == inspect.signature(account.get_self)
