# Runs the app locally or in production using the Waitress server.

import os
import sys
from waitress import serve
from wsgi import application

def main():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    threads = int(os.environ.get("WAITRESS_THREADS", 24))
    channel_timeout = int(os.environ.get("WAITRESS_CHANNEL_TIMEOUT", 60))

    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    print(f"Starting server on http://{host}:{port} ({threads} worker threads)")

    try:
        serve(
            application,
            host=host,
            port=port,
            threads=threads,
            channel_timeout=channel_timeout,
            connection_limit=1000,
            asyncore_use_poll=True
        )
    except KeyboardInterrupt:
        print("\n[+] Graceful shutdown received. Exiting.")
        sys.exit(0)

if __name__ == "__main__":
    main()
