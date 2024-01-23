import logging
import os

logger = logging.getLogger("hatch_openzim")
log_level = logging.getLevelName(os.getenv("HATCH_OPENZIM_LOG_LEVEL", "INFO"))
logger.setLevel(log_level)
