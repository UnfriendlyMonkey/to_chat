import asyncio
import json
import configargparse
from os import environ
from os.path import join, dirname
from dotenv import load_dotenv


def clean_message(message: str) -> bytes:
    replace = message.replace('\\n', '')
    return f'{replace}\n\n'.encode()


async def authorize(reader, writer, token=None):
    if not token:
        token = environ.get('TOKEN')
    print(token)
    hash_prompt = await reader.readline()
    if hash_prompt:
        ask_for_authorization = hash_prompt.decode()
        print(ask_for_authorization, end='')
    if not token:
        token = input('>> ')
    # writer.write(f'{clean_message(token)}\n\n'.encode())
    writer.write(clean_message(token))
    await writer.drain()

    greeting = await reader.readline()
    print(greeting)
    print(type(greeting))
    greeting = json.loads(greeting)

    return greeting


async def tcp_chat_messanger(host: str, port: int):
    reader, writer = await asyncio.open_connection(
        host=host, port=port
    )
    greeting = await authorize(reader, writer)
    print(greeting)
    await reader.readline()
    # message = input()
    # if message:
    #     writer.write(message.encode())
    #     await writer.drain()
    # greetings = await reader.readline()
    # if greetings:
    #     greetings = greetings.decode()
    #     print(greetings, end='')
    while True:
        message = input('>> ')
        if message:
            # writer.write(f'{clean_message(message)}\n\n'.encode())
            writer.write(clean_message(message))
            await writer.drain()

    writer.close()
    await writer.wait_closed()


def parse_arguments():
    parser = configargparse.ArgParser(
        default_config_files=['config.txt'],
        description='''Local chat messanger. After beeing authorized
        you could input you messages for them to appear in local chat'''
    )
    parser.add(
        '-s',
        '--host',
        nargs='?',
        help='host site to be connected to'
    )
    parser.add(
        '-m',
        '--mport',
        type=int,
        nargs='?',
        help='host port to connect to to send messages'
    )
    args = parser.parse_known_args()

    return args


def main():
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    args = parse_arguments()[0]
    print(args)
    host, port = args.host, args.mport
    print(host, port)
    asyncio.run(tcp_chat_messanger(host, port))


if __name__ == '__main__':
    main()