# Importing the logging modules and handlers

import logging
from logging.handlers import RotatingFileHandler
import os
# from vimmo.logger.logging_config import console_handler, file_handler
LOG_DIR = "/home/vincent/Desktop/SoftwareDevelopmentVIMMO/vimmo/logger"
LOG_FILE = "/home/vincent/Desktop/SoftwareDevelopmentVIMMO/vimmo/logger/vimmo.log"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Logger creation

logger = logging.getLogger("VIMMO")
logger.setLevel(logging.DEBUG) # making the default logger at DEBUG level to log all messages

# Defining the formatters

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Handler creation for dual destination logging

# Setting up the console handler for logging to the terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO) # Logs INFO level and  above to the console
console_handler.setFormatter(formatter)

# Setting up the file handler for logging to a file with rotation
file_handler = RotatingFileHandler(os.path.join(LOG_DIR, LOG_FILE), maxBytes=10 * 1024 * 1024, backupCount=3) # This rotates the logs when the file size exceeds 10 MB
file_handler.setLevel(logging.INFO) # Logs DEBUG level and above to the file
file_handler.setFormatter(formatter)

# Adding handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
# def create_connection():
#     """Create a database connection to the database. """
#     try:
#         logger.debug("Attempting to connect to the database.")
#         # raise ConnectionError("Database connection failed.")
#     except Exception as e:
#         logger.error("Database connection error: %s", e)

# if __name__ == "__main__":
#     logger.info("Starting VIMMO")

#     create_connection()

#     logger.info("Shutting down VIMMO")