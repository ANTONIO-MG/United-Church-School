"""Project configuration package: settings, root URLconf and the WSGI/ASGI entry points.

(Celery was removed with the CrewAI media pipeline — the app no longer needs a
task queue. Chat is HTTP-polled and file delivery is plain Django storage.)
"""
