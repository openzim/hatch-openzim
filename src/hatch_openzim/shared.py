import logging
import os
import sys

DEFAULT_FORMAT = "%(name)s:%(levelname)s:%(message)s"

# create logger
logger = logging.getLogger("hatch_openzim")
logger.setLevel(logging.DEBUG)

# setup console logging
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
console_handler.setLevel(os.getenv("HATCH_OPENZIM_LOG_LEVEL", "INFO"))
logger.addHandler(console_handler)
