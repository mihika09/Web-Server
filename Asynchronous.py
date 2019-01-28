import asyncio


async def hello():
    print("Hello")
    await asyncio.sleep(3)
    print("World")


async def main():
    tasks = []
    for _ in range(3):
        tasks.append(asyncio.create_task(hello()))
    for task in tasks:
        await task

if __name__ == '__main__':
    asyncio.run(main())
