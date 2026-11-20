import logging
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
try:
    from edukom_hr.wsgi import application
except Exception:
    logging.getLogger(__name__).exception('Application startup failed')

    def application(environ, start_response):
        body = b'Application temporarily unavailable. Please try again later.'
        start_response('503 Service Unavailable', [('Content-Type', 'text/plain; charset=utf-8'), ('Content-Length', str(len(body))), ('Retry-After', '60')])
        return [body]
