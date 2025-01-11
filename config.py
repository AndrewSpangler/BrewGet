import os

DEBUG = False

APPLICATION_NAME = "Brewget"
APPLICATION_DESCRIPTION = "Multi-System Homebrew Manager"
APPLICATION_DETAILS = "Based on libget / Homebrew Appstore by 4TU"

FOOTER_TEXT = APPLICATION_DESCRIPTION
DEFAULT_DOMAIN = ""
ENVIRONMENT = "test"
TIMEZONE = "US/Pacific"
DOWNLOADS_DIR = "downloads"
# Disable login requirement on login_required pages
LOGIN_DISABLED = False

LOADING_SPLASH = """\n
Welcome to BrewGet!
"""
# Databases
SQLALCHEMY_POOL_SIZE = 24
SQLALCHEMY_MAX_OVERFLOW = 5
SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.getcwd(), "databases/users.sqlite")
# SQLALCHEMY_BINDS = {
# }
# Speeds up database
SQLALCHEMY_TRACK_MODIFICATIONS=False
# SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}
# Folder to output logs too
LOGS_FOLDER = os.path.join(os.getcwd(), "logs")
# File pattern to log to, will become app.log.1, app.log.2 etc when log grows too large
LOG_FILE = os.path.join(LOGS_FOLDER, "app.log")
os.makedirs(LOGS_FOLDER, exist_ok=True)
# Logging Configuration
LOG_CONFIG = (
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s %(name)s %(threadName)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "default",
                "filename": LOG_FILE,
                "maxBytes": 1024 * 1024, # 1 MB max size
                "backupCount": 10,
                "encoding": "utf8",
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["wsgi", "file"]
        },
    }
)