LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default_formatter': {
            'format': '[%(levelname)s:%(asctime)s] %(message)s'
        },
    },
    'handlers': {
        'file': {
            "class": "logging.FileHandler",
            "filename": "nechaev_log.log",
            "formatter": "default_formatter",
            "level": "INFO",
        },
    },
    'loggers': {
        "my_logger": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}