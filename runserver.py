"""
This script runs the pymeWeb application using a development server.
"""

from os import environ
from app import app

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', '0.0.0.0')
    try:
        PORT = int(environ.get('SERVER_PORT', '5551'))
    except ValueError:
        PORT = 5551
    app.run(HOST, PORT, debug=True)
