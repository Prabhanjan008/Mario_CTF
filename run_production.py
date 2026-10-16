"""
Production Server Runner for OJAS Cybersecurity CTF.
Runs the application on Waitress WSGI with optimized multi-threading
and channel buffers capable of serving 100+ concurrent teams.
"""

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

    print("=" * 70)
    print("  [+] MARIO: THE CYBER HEIST - OJAS CTF PRODUCTION SERVER")
    print("  Chanakya University - OJAS Tech Fest 2026")
    print("=" * 70)
    print(f"  * Listening on:          http://{host}:{port}")
    print(f"  * Worker Threads:        {threads}")
    print(f"  * Channel Timeout:       {channel_timeout}s")
    print(f"  * Database Backend:      {'PostgreSQL' if 'postgresql' in os.environ.get('DATABASE_URL', '') else 'SQLite (WAL Mode)'}")
    print(f"  * Concurrency Target:    100+ Teams (Multi-Member Squads)")
    print("=" * 70)
    print("  Starting Waitress Production WSGI Server...")

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
