import logging.config
import os

# Create log directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        # "json": {
        #     "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        #     "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
        # },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
}

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
