# kalshi-python-unofficial

A lightweight Python wrapper for the Kalshi trading API. Fairly untested at the moment.

## Installing
Install with pip: `python3 -m pip install kalshi-python-unofficial`

## Usage
### Setting API Credentials
```python
import kalshi.auth
kalshi.auth.set_key("PUBLIC_KEY","path/to/private_key.pem")
```

### REST Endpoints
Full coverage as of Jan 18th 2025 except for collections and advanced endpoints.
```python
from kalshi.rest import portfolio, exchange
print(portfolio.GetBalance())
print(exchange.GetExchangeStatus())
```

### Websocket Client
```python
import kalshi.websocket
class MyClient(kalshi.websocket.Client):
    async def on_open(self):
        await self.subscribe(["orderbook_delta"], ["KXBTCD-25JAN1821-T104249.99"])

    async def on_message(self, message):
        print("Received message:", message)

ws_client = MyClient()
asyncio.run(ws_client.connect())
```