import asyncio


async def tcp_echo_client():
    reader, writer = await asyncio.open_connection(
            host='minechat.dvmn.org', port=5000
    )
    while True:
        data = await reader.readline()
        print(data)
        message = data.decode()
        if message:
            print(message)
    # TODO: Code is unreachable
    writer.close()
    await writer.wait_closed()


asyncio.run(tcp_echo_client())
