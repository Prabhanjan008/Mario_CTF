"""
WSGI Production Entrypoint for Mario: The Cyber Heist (OJAS CTF).
Exposes 'application' for Waitress, Gunicorn, uWSGI, and mod_wsgi.
"""

import os
from app import create_app

# Instantiate production app
application = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run(host="0.0.0.0", port=port)
