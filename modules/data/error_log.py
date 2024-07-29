import logging
class ErrorLogger:
    def __init__(self, log_file='error_log.txt'):
        self._logging = logging.getLogger(__name__)
        handler = logging.FileHandler(log_file, mode='a')
        handler.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
        handler.setFormatter(formatter)
        self._logging.addHandler(handler)
        self._logging.setLevel(logging.ERROR)

    def log_error(self, error):
        self._logging.error(str(error), exc_info=True)
