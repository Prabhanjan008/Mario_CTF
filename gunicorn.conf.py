"""
Gunicorn Production Configuration for OJAS Cybersecurity CTF.
Optimized for multi-worker Linux / Docker / Kubernetes production deployments.
"""

import os
import multiprocessing

# Network binding
bind = f"{os.environ.get('HOST', '0.0.0.0')}:{os.environ.get('PORT', '5000')}"

# Worker processes & threading
# (2 x CPU cores) + 1 workers, each with 4 threads for high I/O concurrency
workers = int(os.environ.get("GUNICORN_WORKERS", (multiprocessing.cpu_count() * 2) + 1))
threads = int(os.environ.get("GUNICORN_THREADS", 4))
worker_class = "gthread"

# Connection limits
backlog = 2048
max_requests = 10000
max_requests_jitter = 500
timeout = 60
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" (%(D)s µs)'

# Process naming
proc_name = "mario_ojas_ctf"
