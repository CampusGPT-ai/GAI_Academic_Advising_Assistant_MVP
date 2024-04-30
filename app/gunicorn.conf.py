# Gunicorn configuration file
import multiprocessing
import yaml
import os

max_requests = 1000
max_requests_jitter = 50

#with open(os.getenv('LOG_CONFIG_FILE', 'logging.yaml'), 'r') as f:
 #   log_config = yaml.safe_load(f)

#logconfig_dict = log_config

#logconfig_dict['root'] = {
 #   'level': 'WARNING',
 #   'handlers': ['default'],
#}


log_file = "-"

bind = "0.0.0.0:8000"

worker_class = "uvicorn.workers.UvicornWorker"
#workers = (multiprocessing.cpu_count() * 2) + 1
workers = 2

