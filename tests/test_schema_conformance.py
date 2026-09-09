import asyncio
import inspect
import urllib.request

import pytest
import yaml

from fastkalshi.rest.account import Account
from fastkalshi.rest.collection import Collection
from fastkalshi.rest.exchange import Exchange
from fastkalshi.rest.market import Market
from fastkalshi.rest.milestone import Milestone
from fastkalshi.rest.portfolio import Portfolio
from fastkalshi.websocket import Client, KalshiWebSocketError

pytestmark = pytest.mark.schema

OPENAPI_URL = "https://docs.kalshi.com/openapi.yaml"
ASYNCAPI_URL = "https://docs.kalshi.com/asyncapi.yaml"

IMPLEMENTED_OPERATIONS = [
    (Account, "GetLimits", "GetAccountApiLimits", True, set()),
    (Account, "GetEndpointCosts", "GetAccountEndpointCosts", False, set()),
    (
        Collection,
        "GetMultivariateEventCollections",
        "GetMultivariateEventCollections",
        False,
        set(),
    ),
    (
        Collection,
        "GetMultivariateEventCollection",
        "GetMultivariateEventCollection",
        False,
        set(),
    ),
    (Exchange, "GetExchangeSchedule", "GetExchangeSchedule", False, set()),
    (Exchange, "GetExchangeStatus", "GetExchangeStatus", False, set()),
    (Exchange, "GetUserDataTimestamp", "GetUserDataTimestamp", False, set()),
    (Market, "GetEvents", "GetEvents", False, set()),
    (Market, "GetEvent", "GetEvent", False, set()),
    (Market, "GetEventMetadata", "GetEventMetadata", False, set()),
    (Market, "GetEventLiveData", "GetEventLiveData", False, set()),
    (Market, "GetMarkets", "GetMarkets", False, set()),
    (Market, "GetTrades", "GetTrades", False, set()),
    (Market, "GetMarket", "GetMarket", False, set()),
    (Market, "GetMarketOrderbook", "GetMarketOrderbook", True, set()),
    (Market, "GetSeries", "GetSeries", False, set()),
    (Market, "GetMarketCandlesticks", "GetMarketCandlesticks", False, set()),
    (Milestone, "GetMilestones", "GetMilestones", False, set()),
    (Milestone, "GetMilestone", "GetMilestone", False, set()),
    (Milestone, "GetLiveData", "GetLiveDataByMilestone", False, set()),
    (Portfolio, "GetBalance", "GetBalance", True, set()),
    (Portfolio, "GetFills", "GetFills", True, set()),
    (Portfolio, "GetOrders", "GetOrders", True, set()),
    (Portfolio, "GetOrder", "GetOrder", True, set()),
    (Portfolio, "GetOrderQueuePositions", "GetOrderQueuePositions", True, set()),
    (Portfolio, "GetOrderQueuePosition", "GetOrderQueuePosition", True, set()),
    (Portfolio, "GetOrderGroups", "GetOrderGroups", True, set()),
    (
        Portfolio,
        "CreateOrderGroup",
        "CreateOrderGroup",
        True,
        {"contracts_limit"},
    ),
    (Portfolio, "GetOrderGroup", "GetOrderGroup", True, set()),
    (Portfolio, "DeleteOrderGroup", "DeleteOrderGroup", True, set()),
    (Portfolio, "ResetOrderGroup", "ResetOrderGroup", True, set()),
    (Portfolio, "TriggerOrderGroup", "TriggerOrderGroup", True, set()),
    (
        Portfolio,
        "UpdateOrderGroupLimit",
        "UpdateOrderGroupLimit",
        True,
        {"contracts_limit"},
    ),
    (Portfolio, "GetPositions", "GetPositions", True, set()),
    (Portfolio, "GetPortfolioSettlements", "GetSettlements", True, set()),
    (
        Portfolio,
        "GetPortfolioRestingOrderTotalValue",
        "GetPortfolioRestingOrderTotalValue",
        True,
        set(),
    ),
    (
        Portfolio,
        "IntraExchangeInstanceTransfer",
        "IntraExchangeInstanceTransfer",
        True,
        set(),
    ),
    (
        Portfolio,
        "GetIntraExchangeInstanceTransfers",
        "GetIntraExchangeInstanceTransfers",
        True,
        set(),
    ),
    (
        Portfolio,
        "GetIntraExchangeInstanceTransfer",
        "GetIntraExchangeInstanceTransfer",
        True,
        set(),
    ),
    (
        Portfolio,
        "GetTargetBalanceAllocation",
        "GetTargetBalanceAllocation",
        True,
        set(),
    ),
    (Portfolio, "CreateOrder", "CreateOrderV2", True, set()),
    (Portfolio, "BatchCreateOrders", "BatchCreateOrdersV2", True, set()),
    (Portfolio, "AmendOrder", "AmendOrderV2", True, set()),
    (Portfolio, "DecreaseOrder", "DecreaseOrderV2", True, set()),
    (Portfolio, "CancelOrder", "CancelOrderV2", True, set()),
    (Portfolio, "BatchCancelOrders", "BatchCancelOrdersV2", True, set()),
    (Portfolio, "CancelAllOrders", "CancelAllOrders", True, set()),
    (Portfolio, "CreateSubaccount", "CreateSubaccount", True, set()),
    (
        Portfolio,
        "TransferBetweenSubaccounts",
        "ApplySubaccountTransfer",
        True,
        set(),
    ),
    (Portfolio, "GetSubaccountBalances", "GetSubaccountBalances", True, set()),
    (Portfolio, "GetSubaccountTransfers", "GetSubaccountTransfers", True, set()),
]

PARAMETER_ALIASES = {
    (Portfolio, "IntraExchangeInstanceTransfer"): {
        "amount_centicents": "amount",
    }
}


def _load_schema(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return yaml.safe_load(response)


def _resolve(schema, value):
    while isinstance(value, dict) and "$ref" in value:
        reference = value["$ref"]
        value = schema
        for part in reference.split("/")[1:]:
            value = value[part]
    return value


def _openapi_operations(schema):
    operations = {}
    for path, path_item in schema["paths"].items():
        for method, operation in path_item.items():
            if not isinstance(operation, dict) or "operationId" not in operation:
                continue

            parameters = {}
            for raw_parameter in path_item.get("parameters", []) + operation.get(
                "parameters", []
            ):
                parameter = _resolve(schema, raw_parameter)
                parameters[parameter["name"]] = parameter.get("required", False)

            request_body = operation.get("requestBody")
            if request_body:
                request_body = _resolve(schema, request_body)
                content = request_body.get("content", {}).get("application/json")
                if content:
                    body_schema = _resolve(schema, content["schema"])
                    required = set(body_schema.get("required", []))
                    for name in body_schema.get("properties", {}):
                        parameters[name] = name in required

            operations[operation["operationId"]] = {
                "method": method.upper(),
                "path": path,
                "parameters": parameters,
                "authenticated": bool(operation.get("security")),
            }
    return operations


def test_implemented_rest_signatures_match_current_openapi():
    operations = _openapi_operations(_load_schema(OPENAPI_URL))

    for (
        owner,
        method_name,
        operation_id,
        authenticated,
        ignored,
    ) in IMPLEMENTED_OPERATIONS:
        operation = operations[operation_id]
        expected = set(operation["parameters"]) - ignored
        signature = inspect.signature(getattr(owner, method_name))
        aliases = PARAMETER_ALIASES.get((owner, method_name), {})
        actual = {
            aliases.get(name, name) for name in signature.parameters if name != "self"
        }
        supplied = {
            aliases.get(name, name)
            for name, parameter in signature.parameters.items()
            if name != "self"
            and (
                parameter.default is inspect.Parameter.empty
                or parameter.default is not None
            )
        }
        spec_required = {
            name
            for name, is_required in operation["parameters"].items()
            if is_required and name not in ignored
        }

        assert actual == expected, (
            f"{owner.__name__}.{method_name} parameters differ from "
            f"{operation_id} {operation['method']} {operation['path']}"
        )
        assert spec_required <= supplied
        assert operation["authenticated"] is authenticated


class _FakeWebSocket:
    def __init__(self):
        self.closed = None

    async def close(self, code=None, reason=None):
        self.closed = (code, reason)


class _RecordingClient(Client):
    def __init__(self):
        super().__init__()
        self.errors = []

    async def on_error(self, error):
        self.errors.append(error)


def test_orderbook_required_fields_match_current_asyncapi():
    schema = _load_schema(ASYNCAPI_URL)

    for schema_name in ("orderbookSnapshotPayload", "orderbookDeltaPayload"):
        envelope = _resolve(schema, schema["components"]["schemas"][schema_name])
        assert set(envelope["required"]) == {"type", "sid", "seq", "msg"}
        payload = _resolve(schema, envelope["properties"]["msg"])
        assert {"market_ticker", "market_id"} <= set(payload["required"])
        if schema_name == "orderbookDeltaPayload":
            assert {
                "price_dollars",
                "delta_fp",
                "side",
            } <= set(payload["required"])
        assert (
            _resolve(
                schema,
                envelope["properties"]["sid"],
            )["minimum"]
            == 1
        )
        assert (
            _resolve(
                schema,
                envelope["properties"]["seq"],
            )["minimum"]
            == 1
        )


def test_client_rejects_missing_asyncapi_orderbook_fields():
    async def run():
        messages = [
            {
                "type": "orderbook_snapshot",
                "sid": 1,
                "seq": 1,
                "msg": {
                    "market_ticker": "KXTEST",
                    "market_id": "00000000-0000-0000-0000-000000000000",
                },
            },
            {
                "type": "orderbook_delta",
                "sid": 1,
                "seq": 1,
                "msg": {
                    "market_ticker": "KXTEST",
                    "market_id": "00000000-0000-0000-0000-000000000000",
                    "price_dollars": "0.5000",
                    "delta_fp": "1.00",
                    "side": "yes",
                },
            },
        ]

        for message in messages:
            for field in ("sid", "seq", "msg"):
                client = _RecordingClient()
                client.ws = _FakeWebSocket()
                invalid = {**message}
                invalid.pop(field)

                assert await client._handle_protocol_message(invalid) is False
                assert isinstance(client.errors[0], KalshiWebSocketError)
                assert client.ws.closed == (1002, "Invalid message")
            payload_fields = ["market_ticker", "market_id"]
            if message["type"] == "orderbook_delta":
                payload_fields.extend(["price_dollars", "delta_fp", "side"])
            for field in payload_fields:
                client = _RecordingClient()
                client.ws = _FakeWebSocket()
                invalid = {
                    **message,
                    "msg": {**message["msg"]},
                }
                invalid["msg"].pop(field)

                assert await client._handle_protocol_message(invalid) is False
                assert isinstance(client.errors[0], KalshiWebSocketError)
                assert client.ws.closed == (1002, "Invalid message")

    asyncio.run(run())
