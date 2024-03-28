import logging
from pydantic import BaseModel

from config import log_level
import sentry_sdk


LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"


# class LogLevels(BaseModel):
#     info = "INFO"
#     warn = "WARN"
#     error = "ERROR"
#     debug = "DEBUG"


# def configure_logging():
#     log_level = str(LOG_LEVEL).upper()  # cast to string
#     log_levels = list(LogLevels)

#     if log_level not in log_levels:
#         # we use error as the default log level
#         logging.basicConfig(level=LogLevels.error)
#         return

#     if log_level == LogLevels.debug:
#         logging.basicConfig(level=log_level, format=LOG_FORMAT_DEBUG)
#         return

#     logging.basicConfig(level=log_level)


log = logging.getLogger(__name__)

# if server_env != "development":
#     sentry_sdk.init(
#         dsn=sentry_dsn,
#         # Set traces_sample_rate to 1.0 to capture 100%
#         # of transactions for performance monitoring.
#         traces_sample_rate=1.0,
#         # Set profiles_sample_rate to 1.0 to profile 100%
#         # of sampled transactions.
#         # We recommend adjusting this value in production.
#         profiles_sample_rate=1.0,
#     )
