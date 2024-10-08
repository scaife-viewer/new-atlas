#bind=:8000
workers=2
accesslog = "-"
# we need to capture X-Forwarded-For value
access_log_format = '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
loglevel='info'
timeout=60