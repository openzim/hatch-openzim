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
log_level = logging.getLevelName(os.getenv("HATCH_OPENZIM_LOG_LEVEL", "INFO"))
console_handler.setLevel(log_level)
logger.addHandler(console_handler)
