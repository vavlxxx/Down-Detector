import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import settings
from src.gunicorn.app import GunicornApp, get_app_options
from src.main import app


def main():
    GunicornApp(
        app=app,
        options=get_app_options(
            host=settings.gunicorn.GUNICORN_HOST,
            port=settings.gunicorn.GUNICORN_PORT,
            workers=settings.gunicorn.GUNICORN_WORKERS,
            timeout=settings.gunicorn.GUNICORN_TIMEOUT,
            workers_class=settings.gunicorn.GUNICORN_WORKERS_CLASS,
            access_log=settings.gunicorn.GUNICORN_ACCESS_LOG,
            error_log=settings.gunicorn.GUNICORN_ERROR_LOG,
            reload=settings.gunicorn.GUNICORN_RELOAD,
        ),
    ).run()


if __name__ == "__main__":
    main()
