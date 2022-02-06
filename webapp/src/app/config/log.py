###########
# Logging #
###########
import os
import sys
from loguru import logger

log_level = os.environ.get("log_level","INFO")
logger.remove()
logger.add(sys.stderr, level=log_level)
