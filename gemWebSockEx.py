import ssl
import websocket
import json
import base64
import hmac
import hashlib
import time

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

gemini_api_key = "account-iXmg5WhGWCkfXJc1v25H"
gemini_api_secret = "3sKsMT7GEWecDSBse9evp3AsNnam".encode()

payload = {"request": "/v1/marketdata/BTCUSD","nonce": time.time()}
encoded_payload = json.dumps(payload).encode()
b64 = base64.b64encode(encoded_payload)
signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()


ws = websocket.WebSocketApp("wss://api.gemini.com/v1/marketdata/BTCUSD",
                            on_message=on_message,
                            on_error=on_error,
                            header={
                                'Content-Type': 'text/plain',
                                'Content-Length': '0',
                                'X-GEMINI-APIKEY': gemini_api_key,
                                'X-GEMINI-PAYLOAD': b64.decode(),
                                'X-GEMINI-SIGNATURE': signature,
                                'Cache-Control': 'no-cache'
                            })
ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})