import importlib
import threading
from unittest.mock import Mock

from fastkalshi import constants
from fastkalshi.rest import rest
from fastkalshi.rest.market import Market
from fastkalshi.rest.portfolio import Portfolio


def test_discovery_request_does_not_block_mutation_session(monkeypatch):
    constants.use_demo()
    read_started = threading.Event()
    release_read = threading.Event()

    def slow_read(*args, **kwargs):
        read_started.set()
        assert release_read.wait(timeout=2)
        return Mock(status_code=200, content=b'{"markets":[],"cursor":""}')

    write_request = Mock(
        return_value=Mock(
            status_code=201,
            content=(
                b'{"order_id":"1","fill_count":"0.00",'
                b'"remaining_count":"1.00","ts_ms":1}'
            ),
        )
    )
    monkeypatch.setattr(rest.SESSION, "request", slow_read)
    monkeypatch.setattr(rest.WRITE_SESSION, "request", write_request)
    portfolio_module = importlib.import_module("fastkalshi.rest.portfolio")
    monkeypatch.setattr(
        portfolio_module,
        "request_headers",
        lambda method, url: {},
    )

    discovery = threading.Thread(target=Market().GetMarkets)
    discovery.start()
    assert read_started.wait(timeout=1)

    Portfolio().CreateOrder(
        ticker="KXTEST",
        side="bid",
        count="1.00",
        price="0.5000",
        time_in_force="good_till_canceled",
        self_trade_prevention_type="taker_at_cross",
    )

    assert discovery.is_alive()
    assert write_request.call_count == 1
    release_read.set()
    discovery.join(timeout=1)
    assert not discovery.is_alive()
