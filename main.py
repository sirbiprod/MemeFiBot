import asyncio
from contextlib import suppress

from bot.utils.launcher import process

import platform
import sys

def print_versions():
    # Версия Python
    python_version = sys.version
    print(f"Версия Python: {python_version}")

    # Версия системы
    system = platform.system()
    release = platform.release()

    if system == "Windows":
        print(f"Операционная система: {system} {release}")
    elif system == "Linux":
        distro = platform.linux_distribution()
        print(f"Операционная система: {system} {release}")
        print(f"Дистрибутив Linux: {distro[0]} {distro[1]}")
    else:
        print(f"Операционная система: {system} {release}")

async def main():
    await process()


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
