# Logging

The default logging configuration for the python application is defined in `logging.yaml` and provides granular control over the logging of the application and logging of the various libraries used by the application.

## Customizing logging
Set the environment variable `LOG_CONFIG_FILE` to a custom logging configuration file if you wish to override these defaults prior to running the application, e.g.
```bash
export LOG_CONFIG_FILE=my_custom_log_config.yaml
```

### Running with gunicorn
```bash
poetry run gunicorn -c gunicorn.conf.py app:app
```

### Running with uvicorn
```bash
poetry run uvicorn app:app --log-config $LOG_CONFIG_FILE
```


For detailed information on logging configuration options, see [the python documentation](https://docs.python.org/3/library/logging.config.html#configuration-dictionary-schema).
