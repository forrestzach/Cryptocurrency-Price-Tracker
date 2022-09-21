import asyncio
import bittrex
import gemini

async def printBittrex(input):
    print("B-Main system: "+ str(input))
    #pass

async def printGemini(input):
    print("G-Main system: " + str (input))
    pass

async def mainB():
    # mainLoop = asyncio.get_event_loop()
    # if await bittrex.main():
    #     print('bittrex success')
    # else:
    #     print('bittrex fail')

    # if await gemini.runGem():
    #     print('gem success')
    # else:
    #     print('gem fail')

    #await gemini.runGem()
    #await bittrex.main()

    task_B = asyncio.create_task(bittrex.main())
    task_G = asyncio.create_task(gemini.runGem())

    await asyncio.sleep(0.1)

    await task_B
    await task_G
    

   


if __name__ == "__main__":
    asyncio.run(mainB())