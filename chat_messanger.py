import asyncio
import json
import configargparse
import logging
from os import environ
from os.path import join, dirname
from dotenv import load_dotenv


logger = logging.getLogger('messanger')
logging.basicConfig(filename='logging.log', level=logging.DEBUG)


def clean_message(message: str) -> bytes:
    replace = message.replace('\\n', '')
    logger.debug(f'{replace}\n\n'.encode())
    return f'{replace}\n\n'.encode()


async def authorize(reader, writer, token=None):
    if not token:
        token = environ.get('TOKEN')
    # print(token)
    hash_prompt = await reader.readline()
    if hash_prompt:
        ask_for_authorization = hash_prompt.decode()
        logger.debug(ask_for_authorization)
        print(ask_for_authorization, end='')
    if not token:
        token = input('>> ')
    logger.debug(token)
    writer.write(clean_message(token))
    await writer.drain()

    greeting = await reader.readline()
    # print(greeting)
    greeting = json.loads(greeting)

    return greeting


async def register(reader, writer):
    hash_prompt = await reader.readline()
    if hash_prompt:
        logger.debug(hash_prompt)
    writer.write(clean_message(''))
    await writer.drain()
    nickname_prompt = await reader.readline()
    if nickname_prompt:
        nickname_prompt = nickname_prompt.decode()
        logger.debug(nickname_prompt)
        print(nickname_prompt, end='')
    nickname = input()
    logger.debug(nickname)
    writer.write(nickname.encode())
    await writer.drain()
    response = await reader.readline()
    resp_data = json.loads(response)
    new_token = resp_data.get('account_hash', None)
    if new_token:
        with open(join(dirname(__file__), '.env'), 'w') as envfile:
            envfile.write(f'TOKEN={new_token}')


async def tcp_chat_messanger(host: str, port: int):
    logger.debug(f'The Messanger have started working on {host}, {port}')
    reader, writer = await asyncio.open_connection(
        host=host, port=port
    )
    print('Do you want to create a new account or use the existing one?')
    choice = input('Enter "n" to sign up or any other key to sign in: \t')
    if choice.lower() == 'n':
        await register(reader, writer)
        writer.close()
        await writer.wait_closed()
        reader, writer = await asyncio.open_connection(
            host=host, port=port
        )
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    while True:
        greeting = await authorize(reader, writer)
        if greeting:
            logger.debug(greeting)
            print(greeting)
            break
        message = 'Unknown token. Please check it or sign up again'
        print(message)
        logger.debug(message)
    await reader.readline()
    while True:
        message = input('>> ')
        if message:
            logger.debug(message)
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
    args = parse_arguments()[0]
    print(args)
    host, port = args.host, args.mport
    print(host, port)
    asyncio.run(tcp_chat_messanger(host, port))


if __name__ == '__main__':
    main()
