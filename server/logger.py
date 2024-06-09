from rich.logging import RichHandler
import logging

def logger():
    log = logging.getLogger("rich")
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )
    return log