import sys
from loguru import logger
import logging


logger.remove()
logger.add(
    level="DEBUG", 
    sink=sys.stdout, 
    format="<white>{time:YYYY-MM-DD HH:mm:ss}</white>"
                                   " | <level>{level: <8}</level>"
                                   " | <cyan><b>{line}</b></cyan>"
                                   " - <white><b>{message}</b></white>")
logger.add("memefidev.log", level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", rotation="20 MB")

logger = logger.opt(colors=True)
