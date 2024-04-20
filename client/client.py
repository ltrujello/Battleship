import asyncio
import os
from aiohttp import ClientSession, web, WSMsgType

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8080))

BASE_URL = f"http://{HOST}:{PORT}"
WEBSOCKET_URL = "{BASE_URL}/ws"


async def run_client_websocket():
    session = ClientSession()
    async with session.ws_connect(WEBSOCKET_URL) as ws:
        async for msg in ws:
            print(f"Receiving {msg.data=} from incoming websocket connection")
            payload = msg.json()

            if msg.type == WSMsgType.TEXT:
                action = payload["action"]
                handler = handlers[action]
                try:
                    await handler(payload, ws)
                except web.HTTPException as e:
                    resp = {
                        "type": "server_error",
                        "result": "failure",
                        "msg": e.text,
                    }
                    await ws.send_json(resp)
                except Exception as e:
                    resp = {
                        "type": "unknown_error",
                        "result": "failure",
                        "msg": e,
                    }
                    await ws.send_json(resp)

            elif msg.type == WSMsgType.CLOSE:
                await ws.close()

            elif msg.type == WSMsgType.ERROR:
                print("ws connection closed with exception %s" % ws.exception())


if __name__ == "__main__":
    print('Type "exit" to quit')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
