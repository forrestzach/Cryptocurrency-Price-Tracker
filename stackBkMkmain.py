import asyncio
import gemini


async def main():
    gem1 = gemini("wss://api.gemini.com/v1/marketdata/BTCUSD")
    if await gem1.start():
        print('success')
    else:
        print('fail')

asyncio.run(main())