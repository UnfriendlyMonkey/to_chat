import asyncio
import aiofiles
import datetime


def formatted_time():
    now = datetime.datetime.now()
    formatted_datetime = now.strftime('[%d.%m.%y %H:%M]')
    return formatted_datetime


async def tcp_echo_client():
    reader, writer = await asyncio.open_connection(
            host='minechat.dvmn.org', port=5000
    )
    async with aiofiles.open('chatting.log', mode='a') as log_file:
        await log_file.write(f'{formatted_time()} Установлено соединение\n')
        while True:
            # TODO: is there another way to make a loop?
            data = await reader.readline()
            message = data.decode()
            if message:
                print(message, end='')
                await log_file.write(f'{formatted_time()} {message}')
    # TODO: Code is unreachable
    writer.close()
    await writer.wait_closed()


asyncio.run(tcp_echo_client())
