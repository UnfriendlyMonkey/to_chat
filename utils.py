import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def get_asyncio_connection(host: str, port: str) -> None:
    reader, writer = await asyncio.open_connection(
            host=host, port=port
    )
    try:
        yield reader, writer
    finally:
        print('Closing connection')
        writer.close()
        await writer.wait_closed()
        print('Connection closed')
