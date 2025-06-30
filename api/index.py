import sys
import os

from mitraproject.wsgi import application  # pastikan nama sesuai folder/project

# Ini adalah entry point WSGI yang dipakai Vercel
# Tidak perlu handler, cukup `application` saja