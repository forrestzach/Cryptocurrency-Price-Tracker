#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Last tested 2020/09/24 on Python 3.8.5
#
# Note: This file is intended solely for testing purposes and may only be used 
#   as an example to debug and compare with your code. The 3rd party libraries 
#   used in this example may not be suitable for your production use cases.
#   You should always independently verify the security and suitability of any 
#   3rd party library used in your code.

#from csv import QUOTE_NONE
import csv
from signalr_aio import Connection # https://github.com/slazarov/python-signalr-client
from base64 import b64decode
from zlib import decompress, MAX_WBITS
import hashlib
import hmac
import json
import asyncio
import time
import uuid
import brain
import requests
import aiofiles
from aiocsv import AsyncWriter

URL = 'https://socket-v3.bittrex.com/signalr'
API_KEY = 'd5c71de21d4c4f6d9b197863fd0165c4'
API_SECRET = 'ffe55e8ecf034f4e92862025ed84ad24'

HUB = None
LOCK = asyncio.Lock()
INVOCATION_EVENT = None
INVOCATION_RESPONSE = None

tm = time.localtime()
filename = "data/bittrexData_" + str(tm[0]) + "-" + str(tm[1]) + "-" + str(tm[2]) + "_" + str(tm[3]) + "-" + str(tm[4]) + ".csv"

async def startOutput():
  async with aiofiles.open(filename, mode='a',newline="") as outF:
    #aiofiles implementation #await outF.write('\n'.join(str(str(time.time()) + "," + str(jsondata.get('symbol')) + "," + str(jsondata.get('bidRate')) + "," + str(jsondata.get('lastTradeRate')) + "," + str(jsondata.get('askRate')))))
    writer = AsyncWriter(outF, dialect='unix',quoting=csv.QUOTE_NONE)
    await writer.writerow(["TIMESTAMP", "SYMBOL", "BIDRATE", "LASTTRADERATE", "ASKRATE"])

async def getSymbols():
  try: 
    response = requests.get("https://api.bittrex.com/v3/markets", timeout=4)

  except:
    print("failed")

  json_response = json.loads(response.text)
  #print(json_response)
  clearedMarkets = []

  for i in json_response:
    if len(i.get('prohibitedIn')) == 0:
      clearedMarkets.append(i.get('symbol'))

  spiffyMarkets = []
  for i in range(0, len(clearedMarkets), 1):
    if i != 0 or i != len(clearedMarkets):
      if clearedMarkets[i-1].split('-')[0] == clearedMarkets[i].split('-')[0] or clearedMarkets[i+1].split('-')[0] == clearedMarkets[i].split('-')[0]:
        spiffyMarkets.append(clearedMarkets[i])

  symbols = []
  symbols.append('heartbeat')
  for i in spiffyMarkets:
    symbols.append(f'ticker_{i}')
  return symbols

async def main():
  await startOutput()
  await connect()
  if(API_SECRET != ''):
    await authenticate()
  else:
    print('Authentication skipped because API key was not provided')
  await subscribe()
  forever = asyncio.Event()
  await forever.wait()

async def connect():
  global HUB
  connection = Connection(URL)
  HUB = connection.register_hub('c3')
  connection.received += on_message
  connection.error += on_error
  connection.start()
  print('Connected')
 
async def authenticate():
  timestamp = str(int(time.time()) * 1000)
  random_content = str(uuid.uuid4())
  content = timestamp + random_content
  signed_content = hmac.new(API_SECRET.encode(), content.encode(), hashlib.sha512).hexdigest()

  response = await invoke('Authenticate',
    API_KEY,
    timestamp,
    random_content,
    signed_content)

  if response['Success']:
    print('Authenticated')
    HUB.client.on('authenticationExpiring', on_auth_expiring)
  else:
    print('Authentication failed: ' + response['ErrorCode'])

async def subscribe():
  HUB.client.on('heartbeat', on_heartbeat)
  HUB.client.on('trade', on_trade)
  HUB.client.on('ticker', on_ticker)
  HUB.client.on('balance', on_balance)
  # channels = [
  #   'heartbeat',
  #   'ticker_BTC-USD',
  #   'ticker_ETH-BTC',
  #   'ticker_ETH-USD',
  #   'ticker_DOGE-USD',
  #   #'tickers',
  #   'balance'
  # ]
  channels = await getSymbols()

  response = await invoke('Subscribe', channels)
  for i in range(len(channels)):
    if response[i]['Success']:
      print('Subscription to "' + channels[i] + '" successful')
    else:
      print('Subscription to "' + channels[i] + '" failed: ' + response[i]['ErrorCode'])
  
async def invoke(method, *args):
  async with LOCK:
    global INVOCATION_EVENT
    INVOCATION_EVENT = asyncio.Event()
    HUB.server.invoke(method, *args)
    await INVOCATION_EVENT.wait()
    return INVOCATION_RESPONSE

async def on_message(**msg):
  global INVOCATION_RESPONSE
  if 'R' in msg:
    INVOCATION_RESPONSE = msg['R']
    INVOCATION_EVENT.set()

async def on_error(msg):
  print(msg)

async def on_heartbeat(msg):
  print('\u2661')

async def on_auth_expiring(msg):
  print('Authentication expiring...')
  asyncio.create_task(authenticate())

async def on_trade(msg):
  await print_message('Trade', msg)

async def on_balance(msg):
  await print_message('Balance', msg)

async def on_ticker(msg):
  await print_message('Ticker', msg)

async def print_message(title, msg):
  decoded_msg = await process_message(msg[0])
  #print(title + ': ' + json.dumps(decoded_msg, indent = 2))
  #await brain.printBittrex(title + ': ' + json.dumps(decoded_msg, indent = 2))
  await recordData(decoded_msg)

async def process_message(message):
  try:
    decompressed_msg = decompress(b64decode(message, validate=True), -MAX_WBITS)
  except SyntaxError:
    decompressed_msg = decompress(b64decode(message, validate=True))
  return json.loads(decompressed_msg.decode()) 

async def recordData(jsondata):
  #checkout 'aiofiles' on github
  #print("recordData called")
  async with aiofiles.open(filename, mode='a',newline="") as outF:
    #aiofiles implementation #await outF.write('\n'.join(str(str(time.time()) + "," + str(jsondata.get('symbol')) + "," + str(jsondata.get('bidRate')) + "," + str(jsondata.get('lastTradeRate')) + "," + str(jsondata.get('askRate')))))
    writer = AsyncWriter(outF, dialect='unix',quoting=csv.QUOTE_NONE)
    await writer.writerow([time.time(), jsondata.get('symbol'), jsondata.get('bidRate'), jsondata.get('lastTradeRate'), jsondata.get('askRate')])

  #print("recordData finished")
  #pass

if __name__ == "__main__":
  asyncio.run(main())
