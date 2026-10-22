# Serverless function entrypoint for Vercel deployment.

import os
import sys

# Ensure project root is available on sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Force VERCEL environment flag
os.environ["VERCEL"] = "1"

from app import create_app

app = create_app()
