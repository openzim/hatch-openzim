import logging
import os

log = logging.getLogger("hatch_openzim")
log_level = logging.getLevelName(os.getenv("HATCH_OPENZIM_LOG_LEVEL", "INFO"))
log.setLevel(log_level)
