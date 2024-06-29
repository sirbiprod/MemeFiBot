import asyncio
from contextlib import suppress
import sys
from bot.utils.launcher import process


async def main():
    if sys.version_info >= (3,12):
        exit("Python 3.11 or lower is required. Please downgrade your Python version else this code will not work properly.")
    await process()


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
