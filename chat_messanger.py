import asyncio
import json
import configargparse
import logging
import sys
from os import environ
from os.path import join, dirname
from dotenv import load_dotenv


logger = logging.getLogger('messanger')
logging.basicConfig(filename='logging.log', level=logging.DEBUG)


async def authorise(reader, writer, token: str) -> None:
    hash_prompt = await reader.readline()
    if hash_prompt:
        ask_for_authorization = hash_prompt.decode()
        logger.debug(ask_for_authorization)
        print(ask_for_authorization, end='')
    submit_message(writer, token)

    greeting = await reader.readline()
    if not greeting:
        message = 'Unknown token. Please check it or sign up again'
        print(message)
        logger.debug(message)
        sys.exit(1)

    greeting = json.loads(greeting)

    logger.debug(greeting)
    print(greeting)


async def register(reader, writer) -> str:
    hash_prompt = await reader.readline()
    if hash_prompt:
        logger.debug(hash_prompt)
    submit_message(writer, '')
    nickname_prompt = await reader.readline()
    if nickname_prompt:
        nickname_prompt = nickname_prompt.decode()
        logger.debug(nickname_prompt)
        print(nickname_prompt, end='')
    nickname = input()
    submit_message(writer, nickname)
    response = await reader.readline()
    resp_data = json.loads(response)
    new_token = resp_data.get('account_hash', None)
    if new_token:
        with open(join(dirname(__file__), '.env'), 'w') as envfile:
            envfile.write(f'TOKEN={new_token}')
    nickname = resp_data.get('nickname', None)
    print(f'Your new nickname: {nickname} and token: {new_token}')
    return new_token


async def submit_message(writer, message: str) -> None:
    logger.debug(message)
    replace = message.replace('\\n', '')
    replace = f'{replace}\n\n'.encode()
    writer.write(replace)
    await writer.drain()


async def tcp_chat_messanger(host: str, port: int):
    logger.debug(f'The Messanger have started working on {host}, {port}')
    reader, writer = await asyncio.open_connection(
        host=host, port=port
    )
    token = environ.get('TOKEN')
    # print(token)
    # greeting = await authorize(reader, writer, token)
    if not token:
        token = await register(reader, writer)
        writer.close()
        await writer.wait_closed()
        reader, writer = await asyncio.open_connection(
            host=host, port=port
        )
    await authorise(reader, writer, token)

    await reader.readline()
    while True:
        message = input('>> ')
        if message:
            submit_message(writer, message)

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
    args = parse_arguments()[0]
    print(args)
    host, port = args.host, args.mport
    print(host, port)
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    asyncio.run(tcp_chat_messanger(host, port))


if __name__ == '__main__':
    main()
