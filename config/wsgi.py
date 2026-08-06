import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()

# Ensure the persistent disk directories exist at runtime
from django.conf import settings
media_root = getattr(settings, "MEDIA_ROOT", None)
if media_root:
    os.makedirs(media_root, exist_ok=True)
db_path = os.environ.get("DB_PATH")
if db_path:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)