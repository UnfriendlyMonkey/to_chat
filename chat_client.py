import asyncio
import aiofiles
import datetime
import argparse



def formatted_time():
    now = datetime.datetime.now()
    formatted_datetime = now.strftime('[%d.%m.%y %H:%M]')
    return formatted_datetime


async def tcp_echo_client(host, port, history_file):
    reader, writer = await asyncio.open_connection(
            host=host, port=port
    )
    async with aiofiles.open(history_file, mode='a') as log_file:
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


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='''Local chat client.
        Print messages to stdout and save them to file'''
    )
    parser.add_argument(
        '-s',
        '--host',
        nargs='?',
        default='minechat.dvmn.org',
        help='host site to be connected to'
    )
    parser.add_argument(
        '-p',
        '--port',
        type=int,
        nargs='?',
        default=5000,
        help='host port to be connected to'
    )
    parser.add_argument(
        '-y',
        '--history',
        nargs='?',
        default='chatting.log',
        help='file to write chat history to'
    )
    args = parser.parse_args()

    return args


def main():
    args = parse_arguments()
    host, port, history_file = args.host, args.port, args.history
    asyncio.run(tcp_echo_client(host, port, history_file))


if __name__ == '__main__':
    main()
