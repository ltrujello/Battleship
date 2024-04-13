import json
import logging
from aiohttp import web, WSMsgType
from battleship.websocket.handler_map import handlers

LOGGER = logging.getLogger(__name__)


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        LOGGER.info(f"Receiving {msg.data=} from incoming websocket connection")
        payload = json.loads(msg.data)
        user_id = payload["user_id"]
        request.app["websockets"][user_id].add(ws)
        LOGGER.info(f"{request.app['websockets']=}")

        if msg.type == WSMsgType.TEXT:
            action = payload["action"]
            handler = handlers[action]
            try:
                await handler(request, payload, ws)
            except web.HTTPException as e:
                resp = {
                    "type": "server_error",
                    "result": "failure",
                    "msg": e.text,
                }
                await ws.send_str(json.dumps(resp))
            except Exception as e:
                resp = {
                    "type": "unknown_error",
                    "result": "failure",
                    "msg": e,
                }
                await ws.send_str(json.dumps(resp))

        elif msg.type == WSMsgType.CLOSE:
            await ws.close()
            request.app["websockets"][user_id].remove(ws)

        elif msg.type == WSMsgType.ERROR:
            print("ws connection closed with exception %s" % ws.exception())

    print("websocket connection closed")
    return ws
