import ssl
import websockets
import json
import base64
import hmac
import hashlib
import time
import asyncio
import brain

# def on_message(ws, message):
#     print(message)

# def on_error(ws, error):
#     print(error)

# def on_close(ws):
#     print("### closed ###")

uri = 'wss://api.gemini.com/v1/marketdata/btceur'

gemini_api_key = "account-iXmg5WhGWCkfXJc1v25H"
gemini_api_secret = "3sKsMT7GEWecDSBse9evp3AsNnam"


async def connectSock():
    payload = {"request": "/v1/marketdata/btceur","nonce": time.time()}
    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(gemini_api_secret.encode(), b64, hashlib.sha384).hexdigest()

    ws = await websockets.connect(uri,ssl=True,extra_headers={
                                'Content-Type': 'text/plain',
                                'Content-Length': '0',
                                'X-GEMINI-APIKEY': gemini_api_key,
                                'X-GEMINI-PAYLOAD': b64.decode(),
                                'X-GEMINI-SIGNATURE': signature,
                                'Cache-Control': 'no-cache'
                            })
    #getMessages(ws)
    
    #return ws
    print('bleargh')
    async for message in ws:
        
        await brain.printGemini(message)

# async def getMessages(websock):
#     while True:
#         printable  = await websock.recv()
#         print(printable)
#         print('here')

async def runGem():
    #gemLoop = asyncio.get_event_loop()
    #websock = await connectSock()
    await connectSock()
    #await gemLoop.create_task(getMessages(websock))
    #await getMessages(websock)
    #gemLoop.run_forever()
