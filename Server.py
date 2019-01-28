import asyncio
host = '127.0.0.1'
port = 8888


async def echo(reader, writer):

    header = await reader.readuntil(b"\r\n\r\n")
    print("\n===header===\n", header)
    response = "HTTP/1.1 200 OK\r\n"+'Content-Type: text/html\r\n\r\n'+"Hello World!"+'\r\n'
    writer.write(response.encode())
    await writer.drain()
    writer.close()


def execute_server():

    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(echo, host, port)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        print("Shutting down server")

    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


if __name__ == '__main__':

    execute_server()
